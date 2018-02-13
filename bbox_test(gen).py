import bpy, bpy_extras
from mathutils import * # Vector and Matrix and such

d = bpy.data
c = bpy.context
def all(string):
    return [o for o in d.objects if o.name.startswith(string)]

import time
genesis = time.time()
def tick(*a):
    print('[{:.2f}s] '.format(time.time()-genesis)+' '.join(a))

scn = c.scene
cam = d.objects['Camera']

# conversion from world coordinate to screen coordinate
scn = c.scene
active_cam = d.objects['Camera']

def world2screen(loc):
    coord = bpy_extras.object_utils.world_to_camera_view(scn,active_cam,loc)
    return coord

# from https://git.blender.org/gitweb/gitweb.cgi/blender.git/
# blob_plain/HEAD:/release/scripts/modules/bpy_extras/object_utils.py
from mathutils import Vector
def world_to_camera_view(scene, obj, coord):
    """
    Returns the camera space coords for a 3d point.
    (also known as: normalized device coordinates - NDC).

    Where (0, 0) is the bottom left and (1, 1)
    is the top right of the camera frame.
    values outside 0-1 are also supported.
    A negative 'z' value means the point is behind the camera.

    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.

    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg coord: World space location.
    :type coord: :class:`mathutils.Vector`
    :return: a vector where X and Y map to the view plane and
       Z is the depth on the view axis.
    :rtype: :class:`mathutils.Vector`
    """


    co_local = obj.matrix_world.normalized().inverted() * coord
    z = -co_local.z

    camera = obj.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    if camera.type != 'ORTHO':
        if z == 0.0:
            return Vector((0.5, 0.5, 0.0))
        else:
            frame = [(v / (v.z / z)) for v in frame]

    min_x, max_x = frame[1].x, frame[2].x
    min_y, max_y = frame[0].y, frame[1].y

    x = (co_local.x - min_x) / (max_x - min_x)
    y = (co_local.y - min_y) / (max_y - min_y)

    return Vector((x, y, z))

def init_faster_w2c(scene,camobj):
    global w2cm1,w2cframe
    w2cm1 = camobj.matrix_world.normalized().inverted()
    camera = camobj.data
    w2cframe = [-v for v in camera.view_frame(scene=scene)[:3]]
    
def faster_w2c(coord):
    co_local = w2cm1 * coord
    z = - co_local.z
    frame = [(v / (v.z / z)) for v in w2cframe]
    min_x, max_x = frame[1].x, frame[2].x
    min_y, max_y = frame[0].y, frame[1].y

    x = (co_local.x - min_x) / (max_x - min_x)
    y = (co_local.y - min_y) / (max_y - min_y)
    return Vector((x, y, z))

# obtain 12 vertices of the bounding box of an object 
# (deprecated
def bbox_vertices(ob):
    bbox_corners = [ob.matrix_world * Vector(corner) for corner in ob.bound_box]
    return bbox_corners

# obtain all the object's vertices in world coordinate
# (deprecated: loop moved into bbox2d()
def mesh_vertices(ob):
    translated = [ob.matrix_world * vertex.co for vertex in ob.data.vertices]
    return translated

# return the 2d bounding box of an object in scene
def bbox2d(obj):
    #bbv = bbox_vertices(obj)
    # mv = mesh_vertices(obj)
    
    s = obj.data.vertices[0].co
    s = obj.matrix_world*s
    s = world2screen(s)
    maxx,maxy,minx,miny = s.x,s.y,s.x,s.y
    
    for vertex in obj.data.vertices:
        translated = obj.matrix_world*vertex.co
        #s = translated
        v = translated
        #v = world2screen(v)
        v = faster_w2c(v)
        #screen_coords = [world2screen(v) for v in mv]
        #s = screen_coords
        
        # find minmax
        #maxx,maxy,minx,miny = s[0].x, s[0].y, s[0].x, s[0].y    
        
        # check if any of the screen coordinates are behind the camera
        #for v in s:
        if v.z < 0.1:
            return None
        
        if v.x> maxx: 
            maxx = v.x
        elif v.x< minx: 
            minx = v.x
        
        if v.y> maxy:
            maxy = v.y
        elif v.y< miny:
            miny = v.y    
    
    #maxx = max([v.x for v in s])
    #maxy = max([v.y for v in s])
    #minx = min([v.x for v in s])
    #miny = min([v.y for v in s])
    
    # check if the bbox is captured in frame
    if minx>1 or miny>1 or maxx<0 or maxy<0:
        return None
    
    return [minx,miny,maxx,maxy]
    
# render and save image and bbox annotations.
def render_image_and_bbox(destdir, name, bbobjects):
    # specify
    imgdest = destdir + name + '.jpg'
    bpy.data.scenes['Scene'].render.filepath = imgdest
    tick('begin render')
    
    # render and save
    bpy.ops.render.render(write_still=True)
    tick('image into',imgdest)
    
    # save CSV of bbox(es)
    # init w2c translate parameters for camera and scene
    scene = c.scene
    camobj = d.objects['Camera']
    init_faster_w2c(scene, camobj)
    
    csv = ''
    for obj in bbobjects:
        b2d = bbox2d(obj)
        if b2d is not None:
            csv += ','.join([obj.name]+[str(i)for i in b2d]) + '\n'
        else:
            pass
            # don't do anything if no 2d bounding box available for selected object.
            
    csvdest = destdir + name + '.csv'
    with open(csvdest,'w') as f:
        f.write(csv)
    
    tick('csv into:', csvdest)
    
# select all objects that are generated
all_generated = all('gen#')

# specify the destination to save image and bbox annotations
dest_of_generated_images = '/home/qianyonhliang/shapespace/generated_images/'

# render
render_image_and_bbox(dest_of_generated_images, 'test', all_generated)