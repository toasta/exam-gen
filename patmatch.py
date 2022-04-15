import sys
import math
import configparser

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



sheet_f = "process/t.tiff"
_sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)
sheet = _sheet.copy()
sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)


colors = [None for i in range(4)]

#cv is Blue Green Red
colors[0] = (255,0,0)
colors[1] = (0, 255,0)
colors[2] = (0, 0, 255)
colors[3] = (255, 255,0)


barcodes = pyzbar.decode(sheet, symbols=[pyzbar.ZBarSymbol.QRCODE])
assert(len(barcodes) == 1)
barcode = barcodes[0]
x, y , w, h = barcode.rect
center = (int(x+w/2), int(y+h/2))
pxpmm = w/mqr_width
print(f'found qrcode @ {x}/{y} w/ width = {w} px; {mqr_width} => {pxpmm} px/mm')
print(f'poly {barcode.polygon}')


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
        cv2.circle(sheet_debug, (200, 300+i*40), radius=10, color=colors[i], thickness=2)
        print(f'i is {i}, color is {colors[i]}')
    cv2.imwrite("sheet_debug.png", sheet_debug)

p0 = barcode.polygon[0]
p1 = barcode.polygon[1]
p2 = barcode.polygon[2]
p3 = barcode.polygon[3]

print(f'{p0=}')
print(f'{p1=}')
print(f'{p2=}')
print(f'{p3=}')

# "fix"
src_pos.append( (p3.x, p3.y) )
dst_pos.append( (p3.x, p3.y) )

src_pos.append( (p0.x, p0.y) )
dst_pos.append( (p3.x, p0.y) )

src_pos.append( (p2.x, p2.y) )
dst_pos.append( (p2.x, p3.y) )

src_pos.append( (p1.x, p1.y) )
dst_pos.append( (p2.x, p0.y) )


print(f'making homo w/\n{src_pos=}\n{dst_pos=}')

(homo, status) = cv2.findHomography(np.array(src_pos), np.array(dst_pos))
print(homo, status)


sheet = cv2.warpPerspective(_sheet, homo, (_sheet.shape[1]+20, _sheet.shape[0]+20))
sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)


#sys.exit(1)


rs = math.ceil(pxpmm*mark_width)
rs = (rs, rs)

marker = [None for i in range(4)]
tmp = None
for i in range(4):
    #print(f'{i=}')
    t= cv2.imread(f'common/out/{i}.png', cv2.IMREAD_GRAYSCALE)

    # why is this reversed?
    # daaaa.. it is not!!!
    #t=(255 - t)

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

for i in range(4):
    t=match_template(sheet, marker[i], cutoff)
    print(f'{t=}')
    matches[i] = t


for j in range(4):
    _marker= marker[j]
    _match = matches[j]
    nmatch = len(_match[0])
    print(f'{nmatch=} matches for marker {j}')
    for i in range(nmatch):
        (x, y) = _match[1][i], _match[0][i]
        ms_half = int(_marker.shape[1]/2) * 1
        pos=(x + ms_half, y + ms_half)

        #print(f"Draw {pos=} {ms_half=}")
        cv2.circle(sheet_debug, pos, radius=4, color=colors[j], thickness=4)

cv2.imwrite("sheet_debug.png", sheet_debug)
