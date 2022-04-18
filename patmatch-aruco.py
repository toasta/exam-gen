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


barcodes = pyzbar.decode(sheet, symbols=[pyzbar.ZBarSymbol.QRCODE])
assert(len(barcodes) == 1)
barcode = barcodes[0]
x, y , w, h = barcode.rect
center = (int(x+w/2), int(y+h/2))
print(f'found qrcode @ {x}/{y} w/ width = {w} px;')
#print(f'poly {barcode.polygon}, orientation {barcode.orientation}')


# polygon=[Point(x=1706, y=281), Point(x=1708, y=829), Point(x=2253, y=827), Point(x=2253, y=283)], quality=1, orientation='UP')
#poly [Point(x=1170, y=574), Point(x=1534, y=580), Point(x=1540, y=216), Point(x=1175, y=209)]


src_pos = []
dst_pos = []

# 0 top right
# 1 bottom right
# 2 bottom left
# 3 top left
if 1==1:
    for i,_p in enumerate(barcode.polygon):
        p = (_p.x, _p.y)
        cv2.circle(sheet_debug, p, radius=3, color=colors[i], thickness=9)
        #print(f'i is {i}, color is {colors[i]}')
    cv2.imwrite("sheet_debug.png", sheet_debug)

def getpos(polys):
    tmp2 = sorted(polys, key=lambda x: x.y)
    (p0, p1) = sorted(tmp2[:2], key=lambda x: x.x)

    tmp2 = tmp2[2:]
    # simple if would be enough
    tmp2 = sorted(tmp2, key=lambda x: -x.x)

    (p2, p3) = tmp2

    return (p0, p1, p2, p3)

(p0, p1, p2, p3) = getpos(barcode.polygon)


# "fix"
src_pos.append( (p0.x, p0.y) )
dst_pos.append( (p0.x, p0.y) )

src_pos.append( (p1.x, p1.y) )
dst_pos.append( (p1.x, p0.y) )

src_pos.append( (p2.x, p2.y) )
dst_pos.append( (p1.x, p2.y) )

src_pos.append( (p3.x, p3.y) )
dst_pos.append( (p0.x, p3.y) )


print(f'making homo w/\n{src_pos=}\n{dst_pos=}')

(homo, status) = cv2.findHomography(np.array(src_pos), np.array(dst_pos))
print(homo, status)


cv2.imwrite("debug-pre-homo.png", sheet)
if 1==1:
    sheet = _sheet.copy()
else:
    print("rectifying image")
    sheet = cv2.warpPerspective(
        _sheet, homo,
        (_sheet.shape[1]+20, _sheet.shape[0]+20)
        )


#(_, sheet) = cv2.threshold(sheet,92,255,cv2.THRESH_BINARY)

cv2.imwrite("debug-post-homo.png", sheet)

sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)


#sys.exit(1)

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()


(corners, ids, rejected) = cv2.aruco.detectMarkers(sheet, arucoDict, parameters=arucoParams)

ids=ids.flatten()

print(ids)

for (mc, _id) in zip(corners, ids):
    (tl, tr, br, bl) = mc.reshape((4, 2))
    x = int((tl[0] + br[0]) / 2)
    y = int((tr[1] + bl[1]) / 2)
    print(f'marker {_id} @ {x}:{y}')
    col=None
    try:
        col=colors[_id]
    except IndexError:
        col=colors[0]
        pass
    cv2.circle(sheet_debug, (x, y), radius=4, color=col, thickness=2)

#print(corners, ids, rejected)

cv2.imwrite("debug-sheet.png", sheet_debug)
