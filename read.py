#! /usr/bin/env python3

import sys
import json

import dt_apriltags
import cv2
import numpy as np

img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)

det = dt_apriltags.Detector(
    families='tag36h11',
    quad_decimate = 1.0,
    decode_sharpening = 0
)

detections = det.detect(img)

with open("markers.json") as fh:
    markers = json.load(fh)
    id2object = markers['id2object']



res = {
    'line': {},
    'row': {},
}
for i in detections:
    print(i)

    _id = i.tag_id
    center = i.center
    o = id2object[str(_id)]
    ss = o['ss']
    what = o['what']
    if what == 'line':
        line = o['line']
        rep = o['repeat']
        begend = o['beginend']

        if line not in res[what].keys():
            res[what][line] = {}

        if rep not in res[what][line].keys():
            res[what][line][rep] = {}

        res[ what ][ line ][ rep ][ begend ] = int(center[1])
        continue

    if what == 'row':
        row = o['row']
        begend = o['beginend']

        if row not in res[what].keys():
            res[what][row] = {}

        res[ what ][ row ][ begend ] = int(center[0])
        continue



print(json.dumps(res))

square = 20

for line in range(8):
    for row in range(8):
        if row not in res['row'].keys():
            continue
        if line not in res['line'].keys():
            continue

        rep=0

        #TODO linear interpolate that between begin and end and look at x resp. y from that function

        center = [
            res['row'][row]['begin'],
            res['line'][line][rep]['begin'],
        ]

        top_left_x = int(center[0] + square/-2)
        top_left_y = int(center[1] + square/-2)
        bottom_right_x =  int(center[0] + square/2)
        bottom_right_y =  int(center[1] + square/2)

        # opencv/numpy y x 
        avg = np.average(img[top_left_y:bottom_right_y,top_left_x:bottom_right_x])
        checked=False
        if avg < 192:
            checked=True
        print(f'{line+1=}, {rep+1=}, {row+1=}, {avg=}, {checked=}')
