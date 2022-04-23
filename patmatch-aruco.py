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





colors = [None for i in range(4)]

#cv is Blue Green Red
colors[0] = (255,0,0) #  Blue
colors[1] = (0, 255,0) # Green
colors[2] = (0, 0, 255) # Red
colors[3] = (255, 255,0) # teal

def get_markers(img, debug=False):

    # 0 => page corners
    # 1 => columns
    # 2 => begin answers
    # 3 => end answers
    # 4 => line
    #
    a = np.load('common/cd.npz')

    aruco_dict = cv2.aruco.custom_dictionary(int(a['nmarkers']), int(a['markersize']), 0)
    aruco_dict.maxCorrectionBits = int(a['maxCorrectionBits'])
    aruco_dict.bytesList = a['bytesList']

    arucoParams = cv2.aruco.DetectorParameters_create()
    arucoParams.cornerRefinementMaxIterations=64 
    (corners, ids, rejected) = cv2.aruco.detectMarkers(sheet, aruco_dict, parameters=arucoParams)

#    print(corners)
    ids=ids.flatten()
#    print(ids)


    markers = {}


    for (mc, _id) in zip(corners, ids):
        (tl, tr, br, bl) = mc.reshape((4, 2))
        x = int((tl[0] + br[0]) / 2)
        y = int((tr[1] + bl[1]) / 2)

        if _id not in markers.keys():
            markers[_id] = []

        markers[_id].append((x, y))
        if debug:
            col=colors[_id]
            cv2.circle(sheet_debug, (x, y), radius=4, color=col, thickness=2)

    #print(corners, ids, rejected)
    return markers

def get_barcode(sheet):

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
    return barcode


def rectify_image(sheet, markers):
    print(f"rectifying image, {sheet.shape=}")
    dbg1 = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

    markers = markers[0]

    tmp = sorted(markers, key=lambda x: x[1])
    print(f'markers0 sorted by y: {tmp}')

    ss= sheet.shape

    src_pos = []
    dst_pos = []

    # opencv wants y first
    # markers are x,y

    #leftmost
    if tmp[0][0] < tmp[1][0]:
        a=tmp[0]
        b=tmp[1]
    else:
        a=tmp[1]
        b=tmp[0]

    tl=a
    tr=b
    print(f'top:left:{tl}, top:right:{tr}')

    src_pos.append(a)
    dst_pos.append(a)
    src_pos.append(b)
    dst_pos.append((b[0],a[1]))

    if tmp[2][1] < tmp[3][1]:
        a=tmp[2]
        b=tmp[3]
    else:
        a=tmp[3]
        b=tmp[2]

    # bottom left
    print(f'bottom:left:{a}, bottom:right:{b}')
    src_pos.append(a)
    dst_pos.append( (tl[0], a[1]) )

    src_pos.append(b)
    dst_pos.append( (tr[0], a[1]) )

    if 1==0:
        for i,j in enumerate(src_pos):
            cv2.circle(dbg1, j, radius=3, color=colors[i], thickness=9)
        cv2.imwrite("debug/rect-corners.png", dbg1)

    s = np.array(src_pos, dtype=np.float32)
    d = np.array(dst_pos, dtype=np.float32)
    (homo, status) = cv2.findHomography(s, d)
    if 1==0:
        print('source points:')
        print(s)
        print('destination points:')
        print(d)
        print(f'homo for\n{src_pos} =>\n{dst_pos}')
        print(f'{homo=}, {status=}')
    sheet = cv2.warpPerspective(
        sheet, homo,
        (sheet.shape[1]+20, sheet.shape[0]+20)
        )
    cv2.imwrite("debug/post-homo.png", sheet)
    return sheet


def get_question_ranges(sheet, markers):
    begin   = sorted(markers[2], key=lambda x: x[1])
    end     = sorted(markers[3], key=lambda x: x[1])

    print(f'got {len(begin)=} begin markers, {len(end)} end markers')
    assert(len(begin) == len(end))
    ret=[]
    for (i,j) in enumerate(begin):
        ret.append({"yfrom": begin[i][1], 'yto': end[i][1]})

    return ret



if __name__ == '__main__':

    sheet_f = "scans/./200dpi/-000.ppm"
    sheet_f = "process/t.tiff"
    try:
        sheet_f = sys.argv[1]
    except IndexError:
        pass
        

    _sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)
    sheet = _sheet.copy()
    barcode = get_barcode(sheet)
    markers = get_markers(sheet)

    sheet = rectify_image(sheet, markers)
    # reget markers
    markers = get_markers(sheet)
    sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

    for i,j in markers.items():
        for k in j:
            print(k)
            cv2.circle(sheet_debug, k, radius=4, color=colors[3], thickness=2)

    qranges = get_question_ranges(sheet, markers)
    print(qranges)



    cols = markers[1]

    for i in cols:
        cv2.circle(sheet_debug, i, radius=4, color=colors[2], thickness=2)

    if 1==1:
        for i in qranges:
            (yfrom, yto) = (i['yfrom'], i['yto'])
            lines = filter(lambda x: x[1] >= yfrom-10 and x[1] <= yto+10, markers[4])
            for l in lines:
                for c in cols:
                    p=(c[0], l[1])
                    print(p)

                    cv2.circle(sheet_debug, p, radius=4, color=colors[2], thickness=2)

    cv2.imwrite("debug/sheet.png", sheet_debug)
