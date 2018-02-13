import bpy, bgl, blf, mathutils
C = bpy.context
D = bpy.data
from mathutils import *; from math import *

print('traffic genenration script by Qin Yongliang')

scn = C.scene
# car = D.objects['car1']

gen_counter = 0
def remove_obj(obj):
    D.objects.remove(obj,True)
    
def duplicate_obj(obj):
    global gen_counter
    newobj = obj.copy()
    # assign unique name
    gen_counter+=1
    newobj.name = 'gen#' + str(gen_counter)
    
    # link into scene
    scn.objects.link(newobj)
    
    return newobj

def get_all_generated_objects():
    l = []
    for o in D.objects:
        name = o.name
        if 'gen#' in name or 'Model' in name:
            l.append(o)
    return l  

# remove all previously generated objects on start
gened = get_all_generated_objects()
[remove_obj(g) for g in gened]

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
        lof_sampled = random.sample(lof,100)
        
        print('loading from', lof_sampled)
        
        # retrive the object named 'Model' from the various .blend files
        loaded = []
        for model_fn in lof_sampled:
            fullpath = basedir + model_fn
            with bpy.data.libraries.load(fullpath, link=True) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name.startswith('Model')]
            for o in data_to.objects:
                loaded.append(o)
        
        print('loaded models:',len(loaded))
        self.population = loaded
        
    # sample from the population
    def sample(self):
        import random
        newcar = duplicate_obj(random.choice(self.population))
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
basedir = '/home/qianyonhliang/processed/'

car_sampler = ModelSampler(basedir)

def test():
    for i in range(20):
        for j in range (10):
            newcar = car_sampler.sample() # sample from the population of cars
            loc = newcar.location
            loc.x = i * 3.5 # place along a line
            loc.y = j * 9
            loc.z = 0
      
def mask_output():
          
test()
#car_sampler.release()