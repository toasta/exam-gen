import sys
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


colors = [None for i in range(4)]
colors[0] = (255,0,0)
colors[1] = (0, 255,0)
colors[2] = (0, 0, 255)
colors[3] = (255, 255,0)



sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)

barcodes = pyzbar.decode(sheet)
assert(len(barcodes) == 1)
barcode = barcodes[0]
x, y , w, h = barcode.rect
center = (int(x+w/2), int(y+h/2))
pxpmm = w/mqr_width
print(f'found qrcode @ {x}/{y} w/ width = {w} px; {mqr_width} => {pxpmm} px/mm')


rs = int(pxpmm*mark_width)
rs = (rs, rs)

marker = [None for i in range(4)]
tmp = None
for i in range(4):
    #print(f'{i=}')
    t= cv2.imread(f'common/out/{i}.png', cv2.IMREAD_GRAYSCALE)
    t=(255 - t)
    if tmp is None:
        tmp = t
        cv2.imwrite(f'foo.png', t)
    #print(t)
    marker[i] = cv2.resize(t, rs, interpolation = cv2.INTER_NEAREST)

print(f"scaled marker {rs=}, {tmp.shape}")
print(tmp)

if 1==0: 
    with np.printoptions(threshold=np.inf):
        print(marker[0])

sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

match_method = cv2.TM_SQDIFF
match_method = cv2.TM_SQDIFF_NORMED
match_method = cv2.TM_CCOEFF_NORMED

def match_template(img, marker, threshold):
    res = cv2.matchTemplate(img, marker, match_method)
    loc = np.where(res > threshold)
    return loc


matches = [None for i in range(4)]
cutoff=None
#for j in range(100):
for j in range(100):
    cutoff = (71-j) / 100
    t=match_template(sheet, marker[3], match_method)
    nmarkers = len(t[0])
    print(f"trying w/ {cutoff=} => {nmarkers=}")
    if len(t[0]) == 3:
        break

cutoff_limit=.6
if cutoff < cutoff_limit:
    print(f"{cutoff=} < {cutoff_limit=}. something wrong. cowardly exiting")
    sys.exit(1)

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
        #??????
        # marker size
        ms_half = int(_marker.shape[1]/2) * 0
        # - ?????
        pos=(x + ms_half, y + ms_half)

        print(f"Draw {pos=} {ms_half=}")
        cv2.circle(sheet_debug, pos, radius=1, color=colors[j], thickness=4)

cv2.imwrite("sheet_debug.png", sheet_debug)
