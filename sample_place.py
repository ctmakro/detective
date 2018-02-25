import bpy, bgl, blf, mathutils
C = bpy.context
D = bpy.data
from mathutils import *; from math import *
import random

print('traffic genenration script by Qin Yongliang')

scn = C.scene
# car = D.objects['car1']

gen_counter = 0
def remove_obj(obj):
    D.objects.remove(obj,True)

def completely_remove_obj(obj):
    # some lines from https://www.blend4web.com/en/forums/topic/3678/
    # D.objects.remove(obj,True)
    # UNLOAD DATA ! Else name get suffixes.001 .002 AND we have to re-import every object ONE AT A TIME to export them ONE BY ONE.
    # for o in bpy.data.objects:
    #     o.select = True
    
    # deselect all to prevent deletion of unwanted objects.
    bpy.ops.object.select_all(action='DESELECT')
    
    obj.select = True
    bpy.ops.object.delete()   
    #bpy.ops.object.delete()

    # Remove the meshes from memory too
    if obj.data:
        bpy.data.meshes.remove(obj.data, do_unlink=True)
    
    # remove the materials
    for slot in obj.material_slots:
        bpy.data.materials.remove(slot.material, do_unlink=True)
        for texslot in slot.material.texture_slots:
            if texslot:
                bpy.data.textures.remove(texslot.texture, do_unlink=True)
                if texslot.texture.image:
                    bpy.data.images.remove(texslot.texture.image, do_unlink=True)

def duplicate_obj(obj):
    global gen_counter
    newobj = obj.copy()
    # assign unique name
    gen_counter+=1
    newobj.name = 'gen#' + str(gen_counter) + ':' + obj.name
    
    # link into scene
    scn.objects.link(newobj)
    
    return newobj

# every model from shapenet was rescaledp[ since 
# the actual size of model does not matter for shapenet's purpose

# here we assume each bus have uniform width of 2 meters
# and rescale the models accordingly.
def rescale_bus(obj):
    ysize = obj.dimensions.y
    s = 2/ysize
    obj.scale = obj.scale * s
    print(obj.dimensions)

def get_all_generated_objects():
    l = []
    for o in D.objects:
        name = o.name
        if 'gen#' in name or 'Model' in name:
            l.append(o)
    return l  

# remove all previously generated objects on start
# just in case
def remove_all_previously_generated():
    gened = get_all_generated_objects()
    [completely_remove_obj(g) for g in gened]

# load a bunch of .blend files and sample from the population
class ModelSampler:
    def __init__(self, basedir):
        self.sampled = []
        # build the population of cars
        
        # load from .blend files!
        import os,random
        # get our list of .blend files (lof: list of files
        lof = next(os.walk(basedir))[2]
        lof = list(filter(lambda i:i.endswith('.blend'),lof))
        
        # load only some of them (prevents OOM
        lof_sampled = random.sample(lof,50)
        
        # print('loading from', lof_sampled)
        
        # retrive the object named 'Model' from the various .blend files
        loaded = []
        for idx, model_fn in enumerate(lof_sampled):
            fullpath = basedir + model_fn
            print('({}) loading model from'.format(idx), fullpath)
            with bpy.data.libraries.load(fullpath, link=True) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name.startswith('Model')]
            for o in data_to.objects:
                o.name = model_fn # set name of imported object to model filename.
                rescale_bus(o) # rescale the model for correct bus behaviour
                loaded.append(o)
        
        print('loaded models:',len(loaded))
        self.population = loaded
        
    # sample from the population
    def sample(self):
        import random
        chosen = random.choice(self.population)
        newcar = duplicate_obj(chosen)
        # newcar = duplicate_obj(car)
        self.sampled.append(newcar)
        return newcar
    
    # remove samples
    def clear(self):
        for s in self.sampled:
            remove_obj(s)
        self.sampled = []    
        
    # mem release
    def release(self):
        self.clear()
        for p in self.population:
            remove_obj(p)
            # Remove the meshes from memory too
            bpy.data.meshes.remove(p.data, do_unlink=True)
    
# directory where the models reside.
basedir = '/home/qianyonhliang/processed_buses/'

remove_all_previously_generated()
car_sampler = ModelSampler(basedir)

def test():
    for i in range(10):
        for j in range (20):
            newcar = car_sampler.sample() # sample from the population of cars
            loc = newcar.location
            loc.x = i * 14 # place along a line
            loc.y = j * 5
            loc.z = 0
            
            rot = newcar.rotation_euler
            rot.z = random.uniform(-1,1)*0.3
      
test()
#car_sampler.release()
#remove_all_previously_generated()