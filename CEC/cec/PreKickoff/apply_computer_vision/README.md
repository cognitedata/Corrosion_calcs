# Applying Computer Vision for Object Detection

This subdirectory contains scripts and data for running [`YOLO`](https://pjreddie.com/darknet/yolo/),
a real-time object detection system. The current configuration has been adapted from a [tutorial](https://www.pyimagesearch.com/2018/11/12/yolo-object-detection-with-opencv/)
in the `pyimagesearch` blog.

To apply object detection on a video clip, first download the pre-trained weight file into `yolo-coco/` directory:
```
$ wget -X ./yolo-coco/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
```
Then, simply run:
```
$ python yolo_video.py --input input_file.mp4 --output output_file.avi --yolo yolo-coco
```
This will transform `input_file.mp4` into `output_file.avi`, which has object detection results embedded in it.

Before running the command above, make sure all the dependent packages are installed properly. You can do this simply
by following the `poetry` setup outlined in the root directory of this project repo.
