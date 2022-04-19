import sys
import configparser
import json

import numpy as np

import cv2
import cv2.aruco

from pyzbar import pyzbar

CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"



sheet_f = "scans/./200dpi/-000.ppm"
sheet_f = "process/t.tiff"
try:
    sheet_f = sys.argv[1]
except IndexError:
    pass
    

_sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)
sheet = _sheet.copy()
sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)


colors = [None for i in range(4)]

#cv is Blue Green Red
colors[0] = (255,0,0) #  Blue
colors[1] = (0, 255,0) # Green
colors[2] = (0, 0, 255) # Red
colors[3] = (255, 255,0) # teal

def get_markers(img, debug=False):
    a = np.load('common/cd.npz')

    aruco_dict = cv2.aruco.custom_dictionary(int(a['nmarkers']), int(a['markersize']), 0)
    aruco_dict.maxCorrectionBits = int(a['maxCorrectionBits'])
    aruco_dict.bytesList = a['bytesList']

    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(sheet, aruco_dict, parameters=arucoParams)

    print(corners)
    ids=ids.flatten()
    print(ids)


    markers = [[] for i in range(4)]


    for (mc, _id) in zip(corners, ids):
        (tl, tr, br, bl) = mc.reshape((4, 2))
        x = int((tl[0] + br[0]) / 2)
        y = int((tr[1] + bl[1]) / 2)
        if _id >= 0 and _id < 5:
            markers[_id].append((x, y))
            if debug:
                col=colors[_id]
                cv2.circle(sheet_debug, (x, y), radius=4, color=col, thickness=2)

    #print(corners, ids, rejected)
    return markers


barcodes = pyzbar.decode(sheet, symbols=[pyzbar.ZBarSymbol.QRCODE])
assert(len(barcodes) == 1)
barcode = barcodes[0]
x, y , w, h = barcode.rect
center = (int(x+w/2), int(y+h/2))
print(f'found qrcode @ {x}/{y} w/ width = {w} px;')

if 1==0:
    for i,_p in enumerate(barcode.polygon):
        p = (_p.x, _p.y)
        cv2.circle(sheet_debug, p, radius=3, color=colors[i], thickness=9)
        #print(f'i is {i}, color is {colors[i]}')

markers = get_markers(sheet)

src_pos = []
dst_pos = []


m2 = sorted(markers[2], key=lambda x: x[1])
first = m2[0]
src_pos.append( first )
dst_pos.append( first )
if 1==1:
    for j in [1, 2, -1, -2]: 
        i = m2[j]
        a= i
        b= (first[0], i[1])
        src_pos.append( a)
        dst_pos.append( b)
else:
    for i in m2[1:]:
        a= i
        b= (first[0], i[1])
        src_pos.append( a)
        dst_pos.append( b)


print(f'homo for\n{src_pos} =>\n{dst_pos}')
s = np.array(src_pos, dtype=np.float32)
d = np.array(dst_pos, dtype=np.float32)
(homo, status) = cv2.findHomography(s, d)
#homo = cv2.getPerspectiveTransform(s, d)
print(f'{homo=}, {status=}')

assert(homo)

if 1==0:
    sheet = _sheet.copy()
else:
    print("rectifying image")
    cv2.imwrite("debug-pre-homo.png", sheet)
    sheet = cv2.perspectiveTransform( _sheet, homo, (sheet.shape[0] + 1000, sheet.shape[1] + 1000))
    #sheet = cv2.warpPerspective(
    #    _sheet, homo,
    #    (_sheet.shape[1]+20, _sheet.shape[0]+20)
    #    )
    cv2.imwrite("debug-post-homo.png", sheet)


#(_, sheet) = cv2.threshold(sheet,92,255,cv2.THRESH_BINARY)


sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

cv2.imwrite("debug-sheet.png", sheet_debug)

#sys.exit(1)

