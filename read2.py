#! /usr/bin/env python3

import sys
import json
from pyzbar import pyzbar

from PIL import Image, ImageDraw, ImageColor, ImageOps


import dt_apriltags
#import cv2
import numpy as np

#img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
_img = Image.open(sys.argv[1])

c_red = ImageColor.getrgb("#ff0000a0")
c_blue = ImageColor.getrgb("#00ff00a0")
c_green = ImageColor.getrgb("#0000ffa0")

diag1 = _img.copy().convert(mode="RGBA")
diag1_draw = ImageDraw.Draw(diag1)

img = ImageOps.autocontrast(
        ImageOps.grayscale(
        _img
        ))

img = np.array(img)

if 1==1:
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
    nthreads=2,
    quad_decimate = 1.0,
    decode_sharpening = 0.25
)

detections = det.detect(img)

with open("markers-simple.json") as fh:
    markers = json.load(fh)
    id2object = markers['id2object']


#print(json.dumps(id2object))
#sys.exit(1)

markers = []
markers_by_type = {}
markers_by_type_and_value = {}

for i in detections:
    tag_id = i.tag_id
    center = i.center

    o = id2object[str(tag_id)]
    _type = o['what']
    _val = str(o['val'])
    x = int(center[0])
    y = int(center[1])

    diag1_draw.regular_polygon((x, y, 9), n_sides=3, outline=c_blue)

    marker = {'tag_id': tag_id, 'x': x, 'y':y, 'o': o}
    markers.append(marker)

    if _type not in markers_by_type:
        markers_by_type[_type] = []

    markers_by_type[_type].append(marker)



    if _type not in markers_by_type_and_value:
        markers_by_type_and_value[_type] = {}
    if _val not in markers_by_type_and_value[_type]:
        markers_by_type_and_value[_type][_val] = []

    markers_by_type_and_value[_type][_val].append(marker)
    #print(f"marker of type {_type=}, {_val=}, ")

#print(markers)
#print(markers_by_type_and_value['col']['1'][0])

col1markers_ordered =  sorted(
    markers_by_type_and_value['col']['1'],
    key=lambda x: x['y']
)
col2markers_ordered_x =  sorted(
    markers_by_type_and_value['col']['1'],
    key=lambda x: x['x']
)

col3markers_ordered_x =  sorted(
    markers_by_type_and_value['col']['1'],
    key=lambda x: x['x']
)

linemarkers_ordered =  sorted(
    markers_by_type['row'],
    key=lambda x: x['y']
)


        
for i,j in enumerate(col1markers_ordered):
    #print('{}/{}'.format(j['x'], j['y']))
    dist=99999999999999
    thisy = j['y']
    thisx = j['x']
    cols=[]
    cols.append(j)
    lines = []

    if i+1 == len(col1markers_ordered):
        nexty=9999999999
    else:
        nexty=col1markers_ordered[i+1]['y']

    for k in linemarkers_ordered:
        ly = k['y']
        if ly < thisy:
            continue
        if ly >= nexty:
            break
        lines.append(k)

    for k in col2markers_ordered_x:
        if abs(k['y'] - thisy) < 10:
            cols.append(k)

    for k in col3markers_ordered_x:
        if abs(k['y'] - thisy) < 10:
            cols.append(k)

    # get the corresponding qr code
    this_qr = None

    for k in qqr:
        thaty = k['y']
        if thaty >= cols[0]['y'] and thaty <= lines[-1]['y']:
            this_qr = k
            break
    assert(this_qr)

    print('qr at ({} {}) is between col0 w/ y {} and last line y {}'.format(
        this_qr['x'], this_qr['y'],
        cols[0]['y'], lines[-1]['y']
        ))

    # start from the highest col, if ever
    # FIXME - does not work for questions with no correct answer
    # and even if he want's to have this column rated....
    square = 20
    for k in range(3):
        (rx, ry) = (cols[k]['x'], cols[k]['y'])
        for l in lines:
            (lx, ly) = (l['x'], l['y'])
            (mx, my) = (rx, ly)
            #print(f'center ({mx} {my}) .. {c_green=}')
            diag1_draw.ellipse([
                mx+square/-2, my+square/-2,
                mx+square/2, my+square/2
                ], fill=c_green)

                
            avg = int(np.average(img[
                    int(my+square/-2):int(my+square/2),
                    int(mx+square/-2):int(mx+square/2),
                    ]))
            checked=False
            if avg < 200:
                checked=True
            print(f'{checked}')
    diag1.save("foo33.png")


