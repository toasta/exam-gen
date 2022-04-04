#! /usr/bin/env python3

import sys
import json

import dt_apriltags
import cv2
import numpy as np

img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)

det = dt_apriltags.Detector()

res = det.detect(img)

with open("markers.json") as fh:
    markers = json.load(fh)
    id2object = markers['id2object']



for i in res:
    print(f'{i.tag_id} @ {i.center}: {id2object[str(i.tag_id)]["ss"]}')

