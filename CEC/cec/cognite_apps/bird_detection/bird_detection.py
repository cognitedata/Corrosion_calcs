import cv2
import os
import sys
import json
import time
import pafy
import numpy as np

from cognite.client import CogniteClient
from cognite.client.data_classes import Event

args = sys.argv

# Loading camera
if len(args) == 3 and args[1] == '-f':
    # Video File
    path = args[2]
    cap = cv2.VideoCapture(path)
    factor = 5
elif len(args) == 3 and args[1] == '-y':
    # YouTube Video
    url = args[2]
    video = pafy.new(url)
    best = video.getbest(preftype="mp4")
    cap = cv2.VideoCapture(best.url)
    factor = 2
elif len(args) == 2 and args[1] == '-c':
    # Camera
    cap = cv2.VideoCapture(1)
    factor = 1
else:
    print('Usage: bird_detection [-f file | -y youtube-url | -c]')
    exit()

# Loading config
with open("config.json", "r") as f:
    config = json.load(f)
bird_count_time_series_id = config['birdCountTimeSeriesId']
confidence_time_series_id = config['confidenceTimeSeriesId']
size_time_series_id = config['sizeTimeSeriesId']

# Cognite
client = CogniteClient(
    api_key=os.getenv('COGNITE_API_KEY'),
    project=config['project'],
    base_url=config.get('baseUrl'),
    client_name='bird-counter'
)

# Load Yolo
#net = cv2.dnn.readNet("weights/yolov3-tiny.weights", "cfg/yolov3-tiny.cfg")
labelsPath = os.path.sep.join(["yolo-coco", "coco.names"])
weightsPath = os.path.sep.join(["yolo-coco", "yolov3.weights"])
configPath = os.path.sep.join(["yolo-coco", "yolov3.cfg"])
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

classes = []
with open(labelsPath, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

cap_fps = cap.get(cv2.CAP_PROP_FPS) / factor
print('fps {}'.format(cap_fps))
font = cv2.FONT_HERSHEY_PLAIN
starting_time = time.time()
frame_id = 0
while True:
    _, frame = cap.read()
    frame_id += 1
    height, width, channels = frame.shape
    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.1:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.3)
    confidence_datapoints = []
    size_datapoints = []
    count = 0
    t = time.time() * 1000
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = colors[class_ids[i]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(frame, (x, y), (x + w, y + 30), color, -1)
            cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, (255,255,255), 3)

            if label in ['bird', 'kite', 'aeroplane']:
                confidence_datapoints.append((t + count, confidence))
                size_datapoints.append((t + count, w + h))
                count += 1

    print('frame: {}, count: {}'.format(int(cap.get(cv2.CAP_PROP_POS_FRAMES)), count))
    datapoint_list = [{'id': bird_count_time_series_id, 'datapoints': [(t, count)]}]
    if count > 0:
        datapoint_list.append({'id': confidence_time_series_id, 'datapoints': confidence_datapoints})
        datapoint_list.append({'id': size_time_series_id, 'datapoints': size_datapoints})
    client.datapoints.insert_multiple(datapoint_list)

    elapsed_time = time.time() - starting_time
    fps = frame_id / elapsed_time
    cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 3, (0, 0, 0), 3)
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.moveWindow('Image', 0, 0)
    cv2.imshow("Image", frame)
    cap.set(cv2.CAP_PROP_POS_FRAMES, elapsed_time * cap_fps)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()
