import bpy, bgl, blf, mathutils
C = bpy.context
D = bpy.data
O = bpy.ops
from mathutils import *; from math import *

gen_counter = 0
def remove_obj(obj):
    # some lines from https://www.blend4web.com/en/forums/topic/3678/
    # D.objects.remove(obj,True)
    # UNLOAD DATA ! Else name get suffixes.001 .002 AND we have to re-import every object ONE AT A TIME to export them ONE BY ONE.
    # for o in bpy.data.objects:
    #     o.select = True
    obj.select = True
    O.object.delete()   
    #bpy.ops.object.delete()

    # Remove the meshes from memory too
    bpy.data.meshes.remove(obj.data, do_unlink=True)
    
    #for mesh in bpy.data.meshes:
    #    bpy.data.meshes.remove(mesh, do_unlink=True)
    #    print(meshes_to_remove)
    
def duplicate_obj(obj):
    global gen_counter
    newobj = obj.copy()
    # assign unique name
    gen_counter+=1
    newobj.name = 'gen#' + str(gen_counter)
    
    # link into scene
    scn.objects.link(newobj)
    
    return newobj

# -----

# takes OBJ models and outputs .blend files for
# later inclusion from other scenes.
print('model processing script by Qin Yongliang')

scn = C.scene
# car = D.objects['car1']

def n(name):
    return D.objects[name]


def all_mesh_obj():
    return list(filter(lambda o:'mesh'in o.name, D.objects))

# find all meshes in the imported model
def join_all_into_one():
    meshes = all_mesh_obj()

    print('found', len(meshes), 'meshes.')

    if len(meshes)<1:
        print('nothing to join() since no "mesh"es found...')
    else:
        # print(all_mesh_obj())  

        # select them all
        for m in meshes:
            m.select = True
        # active select one of them to prevent 
        # lack of context error from join()   
        scn.objects.active = meshes[0]
            
        print(len(meshes), 'meshes selected.')
        
        # join them into one object
        O.object.join()
        print('meshes joined into one.')

        # rename the remaining mesh to make life easier...
        leftover = scn.objects.active
        leftover.name = 'Model'
        print('name of active object changed to:',leftover.name)

# scale up to meters (approximate.
def upscale():
    m = D.objects['Model']
    if m.scale.x <1.1:
        m.scale = [8,8,8]
        print(m.scale)
    else:
        print('no need to upscale...')

# apply(therefore remove) all transfomations
# move the origin to the bottom of the bounding box of the object
def re_origin():
    m = D.objects['Model']
    m.select = True
    O.object.transform_apply(rotation=True, scale=True)
    O.object.origin_set(type='GEOMETRY_ORIGIN',center='BOUNDS')
    m.location = [0,0,0]

    # now move cursor to the bottom of the bbox
    height = m.dimensions.z
    print('height of object bbox:', height)
    dest_z = m.location.z - height/2
    C.scene.cursor_location = [m.location.x, m.location.y, dest_z]
    
    # now move origin of object to cursor
    O.object.origin_set(type='ORIGIN_CURSOR',center='BOUNDS')
    
    # move object back to center of world
    m.location = [0,0,0]
    print('origin adjusted...')

def get_home():
    from os.path import expanduser
    home = expanduser('~')
    return home

# save current .blend to a specified destination
destdir = get_home() + '/processed/'

def save_as(namestr):
    fullpath = destdir + namestr + '.blend'
    bpy.ops.wm.save_as_mainfile(
        filepath = fullpath,
        check_existing = False,
        compress = True,
        copy = True,
        relative_remap = True,
    )
    print('current working state should be saved to', fullpath)

def import_obj(path):
    imported = bpy.ops.import_scene.obj(filepath=path)
    print('imported:',imported)

# path to directories to scan
basedir = '/home/qianyonhliang/shapespace/02801938/'

def main():
    # scan all dirs, process and save the model.obj found under each dir
    import os
    all_dirs = next(os.walk(basedir))[1]
    print('found',len(all_dirs),'directories under', basedir)

    for subdir in all_dirs:
        
        key = subdir
        import_obj(basedir+key+'/model.obj')
        join_all_into_one()
        upscale()
        re_origin()
        save_as(key)
        
        remove_obj(D.objects['Model'])
        
main()
