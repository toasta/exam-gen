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


#print(json.dumps(id2object))
#sys.exit(1)

res = {
    'line': {},
    'row': {},
}
for i in detections:
    print(i)

    _id = i.tag_id
    center = i.center
    o = id2object[str(_id)]
    print(json.dumps(o, indent=1))
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

        res[ what ][ line ][ rep ][ begend ] = center
        continue

    if what == 'row':
        row = o['row']
        begend = o['beginend']

        if row not in res[what].keys():
            res[what][row] = {}

        res[ what ][ row ][ begend ] = center
        continue




# https://stackoverflow.com/questions/3252194/numpy-and-line-intersections
def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return (float('inf'), float('inf'))
    return (x/z, y/z)


square = 22


for line in range(8):
    for row in range(2,5):
        if row not in res['row'].keys():
            continue
        if line not in res['line'].keys():
            continue

        rep=0

        isect = get_intersect(
            res['row'][row]['end'],
            res['row'][row]['begin'],
            res['line'][line][rep]['end'],
            res['line'][line][rep]['begin'],
            )

        # TODO --- add empty lines so we can get 'gray average value' of just the square (227 here)

        # opencv/numpy y x 
        avg = int(np.average(img[
            int(isect[1]+square/-2):int(isect[1]+square/2),
            int(isect[0]+square/-2):int(isect[0]+square/2),
            ]))
        checked=False
        if avg < 200:
            checked=True
        print(f'{line+1=}, {rep+1=}, {row+1=}, {avg=}, {checked=}')
