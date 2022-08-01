# Bird counting using YOLOv3

This demo code counts the number of birds in video files, YouTube videos or PC camera input, and store the statistics to CDF. It detects 'bird', 'kite' and 'aeroplane' objects on the COCO data set with an implementation YOLOv3 (because birds sometimes look like kites or aeroplanes!).

It process a video stream in real-time, and you can see the results in your Grafana dashboard.

<img src="images/video.png" style="width: 320px; vertical-align: middle;"> <img src="images/grafana.png" style="width: 374px; vertical-align: middle;">

## Installation

We need opencv-python and pafy installed.

```bash
pip install opencv-python pafy
```

Download the pre-trained weight file into `yolo-coco/` directory:

```bash
wget -X ./yolo-coco/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
```

## Prerequisites

Create 3 time series in your CDF project and note their IDs.

- bird count
- confidence
- bounding box size

Edit config.json for your CDF project.

Property | Description
-- | --
project | Your CDF project
baseUrl | Your CDF cluster base URL (defaults to https://api.cognitedata.com)
birdCountTimeSeriesId | Time series ID for the bird count
confidenceTimeSeriesId | Time series ID for the confidence
sizeTimeSeriesId | Time series ID for the bounding box size

Setup your grafana dashboard based on [this configuration JSON file](grafana_dashboard.json). In Grafana, go to Dashboard > Settings > JSON Model, paste the JSON and click 'Save changes'. Then, edit the time series of each panel for your CDF project.

## Run

Set the `COGNITE_API_KEY` environment variable to your API key.

**Note:** This demo code doesn't support OIDC, but you can modify the `CogniteClient` initialization code to support OIDC.

For video files:
```bash
python bird_detection.py -f <video file>
```

For YouTube videos:
```bash
python bird_detection.py -y <youtube url such as https://www.youtube.com/watch?v=qGlH6H9l85U>
```

For Camera input:
```bash
python bird_detection.py -c
```

**Note:** You may see the following error when specifying YouTube videos. This is because the Pafy module is outdated and doesn't follow the recent changes in YouTube.

```bash
Traceback (most recent call last):
  File "/Users/akusanagi/projects/sumitomo-bird-detection/bird_detection.py", line 23, in <module>
    video = pafy.new(url)
  File "/usr/local/lib/python3.9/site-packages/pafy/pafy.py", line 124, in new
    return Pafy(url, basic, gdata, size, callback, ydl_opts=ydl_opts)
  File "/usr/local/lib/python3.9/site-packages/pafy/backend_youtube_dl.py", line 31, in __init__
    super(YtdlPafy, self).__init__(*args, **kwargs)
  File "/usr/local/lib/python3.9/site-packages/pafy/backend_shared.py", line 97, in __init__
    self._fetch_basic()
  File "/usr/local/lib/python3.9/site-packages/pafy/backend_youtube_dl.py", line 54, in _fetch_basic
    self._dislikes = self._ydl_info['dislike_count']
KeyError: 'dislike_count'
```

To fix it, edit the line 53 and 54 in `pafy/backend_youtube_dl.py` stated above as follows.

```py
        self._likes = self._ydl_info.get('like_count', 0)
        self._dislikes = self._ydl_info.get('dislike_count', 0)
```
