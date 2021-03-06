import sys
import math
import configparser
import json

import numpy as np

import cv2

from pyzbar import pyzbar

CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"

mqr_width  = CFG[SECTION]['MAIN_QR_WIDTH']
if not mqr_width.endswith('mm'):
    print("specify main qr code size in mm (!)")
    sys.exit(1)

mqr_width  = int(mqr_width.rstrip('m'))
mark_width = CFG[SECTION]['MARKER_WIDTH']
if not mark_width.endswith('mm'):
    print("specify mark size in mm (!)")
    sys.exit(1)

mark_width  = int(mark_width.rstrip('m'))




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
pxpmm = w/mqr_width
print(f'found qrcode @ {x}/{y} w/ width = {w} px; {mqr_width} => {pxpmm} px/mm')
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


rs = math.ceil(pxpmm*mark_width)
marker_size=rs
rs = (rs, rs)
print(f"markers will be rescaled from {mark_width} to {rs}")

marker = [None for i in range(4)]
tmp = None
for i in range(4):
    #print(f'{i=}')
    t= cv2.imread(f'common/out/{i}.png', cv2.IMREAD_GRAYSCALE)

    marker[i] = cv2.resize(t, rs, interpolation = cv2.INTER_NEAREST)

    if 1==1:
        cv2.imwrite(f'debug-marker{i}.png', t)
        cv2.imwrite(f'debug-marker{i}-resized.png', marker[i])
    #print(t)

#print(f"scaled marker {rs=}, {tmp.shape}")

if 1 == 0: 
    with np.printoptions(threshold=np.inf):
        print(marker[0])


#match_method = cv2.TM_SQDIFF
match_method = cv2.TM_SQDIFF_NORMED
#match_method = cv2.TM_CCOEFF_NORMED
match_method = cv2.TM_CCORR_NORMED

def match_template(img, marker, threshold=.9, return_res=False):
    res = cv2.matchTemplate(img, marker, match_method)
    if return_res:
        return res

    loc = np.where(res > threshold)

    #print(f'returning {loc=}')
    return loc


matches = [None for i in range(4)]
cutoff=None
#for j in range(100):
if 1==1:
    t=match_template(sheet, marker[0], return_res=True)
    merk = None
    found = False
    for j in range(100, 60, -1):

        cutoff = j / 100
        loc = np.where(t > cutoff)
        nmarkers = len(loc[0])
        print(f'{nmarkers=} @ {cutoff=}')

        if nmarkers >= 3:
            break

matches[0] = match_template(sheet, marker[0], cutoff)


if 1==0:
    for j in range(100, 60, -1):
        cutoff = j / 100
        t1=match_template(sheet, marker[1], match_method, return_res=True)
        t2=match_template(sheet, marker[3], match_method, return_res=True)
        n1 = len((np.where(t1 > cutoff))[0])
        n2 = len((np.where(t2 > cutoff))[0])
        if 1==1:
            print(f'marker2 {n1}, marker3 {n2} @ cutoff {cutoff}')
        if n1 and n1==n2:
            break

cutoff=.80

matches[1] = match_template(sheet, marker[1], cutoff)
matches[2] = match_template(sheet, marker[2], cutoff)
matches[3] = match_template(sheet, marker[3], cutoff)


#assert(len(mo[0]) == 3)
def merge_points2(m):
    mdiff = 4
    for i in range(len(m)):
        pass

def merge_points(m):
    pp = []
    for i in range(len(m[0])):
        (y, x) = (m[0][i], m[1][i])
        pp.append([x, y])
    #found=False
    #pp3 = []
    #pp2 = sorted(pp, key=lambda x: x[0])

    print(f'current number of points: {len(pp)=}')

    pp2=[]
    # TODO do this in np
    # this is quadratic
    while True:

        found=False
        for i in range(len(pp)):
            print(f"points {i}")

            x = _x = pp[i][0]
            y = _y = pp[i][1]

            co = 0
            for j in range(len(pp)):

                dist=abs(_x - pp[j][0]) + abs(_y - pp[j][1])

                if dist > 4:
                    pp2.append(pp[i])
                    continue

                #print(f'diff {i} against {j} {dist1=} {dist2=}')
                found=True

                x += pp[j][0]
                y += pp[j][1]
                co += 1

        if found:
            pp2.append([x//co, y//co])
        else:
            break

    print(f'cleaned number of points: {len(pp2)=}')
    return pp2
        
#matches[2] = merge_points(matches[2])
    

if 1==1:
    for j in [0,1,3,2]:
        nmatch = len(matches[j][0])
        print(f'{nmatch=} matches for marker {j}')
        for i in range(nmatch):
            (y, x) = (matches[j][0][i], matches[j][1][i])
            x += 1
            y += 1
            #fak=1
            #y = int(y//fak * fak + fak/2)
            #x = int(x//fak * fak + fak/2)
            o = f'{x//2}/{y//2}'


            ms_half = int(marker[j].shape[1]/2) * 1 
            pos=(int(x + ms_half), int(y + ms_half))

            print(f"Draw {pos=}")
            cv2.circle(sheet_debug, pos, radius=marker[j].shape[0]//2, color=colors[j], thickness=2)

cv2.imwrite("debug-sheet.png", sheet_debug)
