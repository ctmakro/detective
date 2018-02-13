import bpy, bpy_extras
from mathutils import * # Vector and Matrix and such

d = bpy.data
c = bpy.context
def all():
    return [o for o in d.objects if o.name.startswith('Cub')]

allcube = all()

print(allcube)

scn = c.scene
cam = d.objects['Camera']

# conversion from world coordinate to screen coordinate
def world2screen(loc):
    scn = c.scene
    cam = d.objects['Camera']
    coord = bpy_extras.object_utils.world_to_camera_view(scn,cam,loc)
    return coord

# obtain 12 vertices of the bounding box of an object 
# (deprecated
def bbox_vertices(ob):
    bbox_corners = [ob.matrix_world * Vector(corner) for corner in ob.bound_box]
    return bbox_corners

# obtain all the object's vertices in world coordinate
def mesh_vertices(ob):
    translated = [ob.matrix_world * vertex.co for vertex in ob.data.vertices]
    return translated

# return the 2d bounding box of an object in scene
def bbox2d(obj):
    #bbv = bbox_vertices(obj)
    mv = mesh_vertices(obj)
    screen_coords = [world2screen(v) for v in mv]
    s = screen_coords
    maxx = max([v.x for v in s])
    maxy = max([v.y for v in s])
    minx = min([v.x for v in s])
    miny = min([v.y for v in s])
    
    return [minx,miny,maxx,maxy]
    
# render and save image and bbox annotations.
def render_image_and_bbox(destdir, name, bbobjects):
    # specify
    imgdest = destdir + name + '.jpg'
    bpy.data.scenes['Scene'].render.filepath = imgdest
    # render and save
    bpy.ops.render.render(write_still=True)
    
    # save CSV of bbox(es)
    csv = ''
    for obj in bbobjects:
        b2d = bbox2d(obj)
        csv += ','.join([obj.name]+[str(i)for i in b2d]) + '\n'
    
    csvdest = destdir + name + '.csv'
    with open(csvdest,'w') as f:
        f.write(csv)
    
    print('image into:', imgdest)
    print('csv into:', csvdest)
     
# demo
def unused():
    for obj in allcube:
        b2d = bbox2d(obj)
        print(','.join([obj.name]+b2d))
        
render_image_and_bbox('/home/qianyonhliang/shapespace/generated_images/', 'test', allcube)