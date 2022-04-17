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




sheet_f = "scans/one-test/0.png"
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
if 1==0:
    for i,_p in enumerate(barcode.polygon):
        p = (_p.x, _p.y)
        cv2.circle(sheet_debug, p, radius=3, color=colors[i], thickness=9)
        cv2.circle(sheet_debug, (200, 300+i*40), radius=10, color=colors[i], thickness=2)
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
sheet = cv2.warpPerspective(
    _sheet, homo,
    (_sheet.shape[1]+20, _sheet.shape[0]+20)
    )
cv2.imwrite("debug-post-homo.png", sheet)

sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)


#sys.exit(1)


rs = math.ceil(pxpmm*mark_width)
marker_size=rs
rs = (rs, rs)

marker = [None for i in range(4)]
tmp = None
for i in range(4):
    #print(f'{i=}')
    t= cv2.imread(f'common/out/{i}.png', cv2.IMREAD_GRAYSCALE)

    marker[i] = cv2.resize(t, rs, interpolation = cv2.INTER_NEAREST)

    if 1==0:
        cv2.imwrite(f'debug-marker{i}.png', t)
        cv2.imwrite(f'debug-marker{i}-resized.png', marker[i])
    #print(t)

#print(f"scaled marker {rs=}, {tmp.shape}")

if 1 == 0: 
    with np.printoptions(threshold=np.inf):
        print(marker[0])


#match_method = cv2.TM_SQDIFF
#match_method = cv2.TM_SQDIFF_NORMED
#match_method = cv2.TM_CCOEFF_NORMED
match_method = cv2.TM_CCORR_NORMED

def match_template(img, marker, threshold, return_res=False):
    res = cv2.matchTemplate(img, marker, match_method)
    if return_res:
        return res
    loc = np.where(res > threshold)
    return loc


matches = [None for i in range(4)]
cutoff=None
cutoff_limit=.6
#for j in range(100):
if 1==0:
    t=match_template(sheet, marker[0], match_method, return_res=True)
    for j in range(100):
        cutoff = (100-j) / 100

        if cutoff < cutoff_limit:
            print(f"{cutoff=} < {cutoff_limit=}. something wrong. cowardly exiting")
            sys.exit(1)
        loc = np.where(t > cutoff)
        nmarkers = len(loc[0])
        print(f"{cutoff=} => {nmarkers=}")
        # should be exactly thre.....
        if nmarkers >= 3:
            break
cutoff = .90


print(f'running w/ {cutoff=}')

# TODO -- match only the top left, bottom right markers.
# then get all the line markers in this rect
#
mo = [None for i in range(4)]
molo = set()



for i in range(4):
    t=match_template(sheet, marker[i], cutoff)
    print(f'{t=}')
    matches[i] = t
    mo[i] = []
    for j in range(len(t[0])):

        (x, y) = (t[1][j], t[0][j])
        o = { 'x': x, 'y': y }
        _id = "/".join([str(i), str(o['x']), str(o['y'])])
        if _id not in molo:
            molo.add(_id)
            mo[i].append(o)

#assert(len(mo[0]) == 3)

mak = {}

mak['column'] = mo[0]
mak['startlo'] = mo[1]
mak['line'] = mo[2]
mak['endbr'] = mo[3]

print(json.dumps(mak, indent=1))

if 1==1:
    for j in range(4):
        nmatch = len(mo[j])
        print(f'{nmatch=} matches for marker {j}')
        for i in mo[j]:
            (x, y) = (i['x'], i['y'])
            ms_half = int(marker[j].shape[1]/2) * 1
            pos=(x + ms_half, y + ms_half)

            #print(f"Draw {pos=} {ms_half=}")
            cv2.circle(sheet_debug, pos, radius=4, color=colors[j], thickness=4)

cv2.imwrite("sheet_debug.png", sheet_debug)
