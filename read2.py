#! /usr/bin/env python3




import sys
import json
from pyzbar import pyzbar


import dt_apriltags
import cv2
import numpy as np

img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)

if 1==0:
    barcodes = pyzbar.decode(img)


    qqr = []
    for barcode in barcodes:
        x, y , w, h = barcode.rect
        center = (int(x+w/2), int(y+h/2))
        qqr.append({ 'x': center[0], 'y':center[1], 'bc': barcode})

    #print(f'found {len(qqr)} barcodes; centers:{lambda x: f"" } ')
    print(f'found {len(qqr)} barcodes:')
    tmp = []
    for i in qqr:
        tmp.append('({} {})'.format(i['x'],i['y']))
    print(",".join(tmp))

det = dt_apriltags.Detector(
    families='tag16h5',
    quad_decimate = 1.0,
    decode_sharpening = 0
)

detections = det.detect(img)

with open("markers-simple.json") as fh:
    markers = json.load(fh)
    id2object = markers['id2object']


#print(json.dumps(id2object))
#sys.exit(1)

markers = []
for i in detections:
    _id = i.tag_id
    center = i.center
    markers.append({'_id': _id, 'x': center[0], 'y': center[1], 'obj': i})

print("___________________________________________________")
#print(markers)

# scan all 'Row1' Markers.
# each
#  go down to til linemarkers (rows?) does not increase anymore
#  record qr-code seen while going down.
#  now search between columnmarker0 and linemarker[-1] 
#



markers_by_type = {}
markers_by_type_and_value = {}

for i in markers:
    _id = i['_id']
    o = id2object[str(_id)]
    _type = o['what']
    _val = str(o['val'])
    o['obj'] = i

    if _type not in markers_by_type:
        markers_by_type[_type] = []

    markers_by_type[_type].append(o)



    if _type not in markers_by_type_and_value:
        markers_by_type_and_value[_type] = {}
    if _val not in markers_by_type_and_value[_type]:
        markers_by_type_and_value[_type][_val] = []

    markers_by_type_and_value[_type][_val].append(o)

print(markers_by_type_and_value['col']['1'][0])

col1markers_ordered =  sorted(markers_by_type_and_value['col']['1'],
    key=lambda x: x['obj']['y']
)

        
for i in col1markers_ordered:
    print('{}/{}'.format(i['obj']['x'], i['obj']['y']))





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


def do_count():
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
