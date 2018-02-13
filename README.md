# Detective

Blender scripts for data generation for object detection in deep learning.

## Requirements

- Blender 2.79 please
- Start Blender from commandline (such that you can get feedbacks from whatever script you were running)
- some ShapeNet models

## Convert ShapeNet models into Blender format

For easier later consumption.

ShapeNet models are usually organized as follows:

```text
/02948288
----/b2ab08bad88e...
----/c498cde98654...
--------/model.obj
--------/model.mtl
------------/images
```

1. open `model_preprocess.blend` in Blender

2. modify the path specified in your script to a directory like `/users/yourname/shapenet/02948288/`

3. modify another path specified in your script to a directory like `/users/yourname/output/`

4. Run the script. Blender will attempt to import each `model.obj` from the source directory and save them into `.blend` files. Will take a while if the number of models within the directory is large.

## Import converted models into Blender

And make an army of them!

1. open `scene_generator.blend` in Blender

2. There're two scripts: Run one of them to randomly load 100 models from the directory, and place them randomly in current scene.

    (before run, modify the paths to load from a directory that contains a lot of converted models. )

    (If the number of models within the directory is less than 100, i don't know/care what will happen.)

3. run another script to render an Image and save it along with its bounding box descriptions (in CSV format), for models in front of the camera.

    (before run, modify the paths to save to a directory of your interest.)

## Visualize rendered image with bounding boxes

- please refer to `visualize_bbox.py` (run with Python, not Blender).
- you will need `opencv-python` to run this script.
