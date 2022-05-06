import sys
import configparser
import json

import numpy as np

import cv2
import cv2.aruco

from pyzbar import pyzbar
from lib import Mcolor

CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"




mcolor = Mcolor.Mcolor(angle_increment=360/10)

def get_markers(img, debug=False):

    # 0 => page corners
    # 1 => columns
    # 2 => qmarker
    # 4 => line
    #
    a = np.load('common/cd.npz')

    aruco_dict = cv2.aruco.custom_dictionary(
        int(a['nmarkers']), int(a['markersize']), 0)
    aruco_dict.maxCorrectionBits = int(a['maxCorrectionBits'])
    aruco_dict.bytesList = a['bytesList']

    arucoParams = cv2.aruco.DetectorParameters_create()
    if 1==0:
        arucoParams.maxMarkerPerimeterRate          = 8
        arucoParams.minMarkerDistanceRate           = 0.00000000001
        arucoParams.minCornerDistanceRate = 0.00000000001
        arucoParams.minMarkerDistanceRate = 0.00000000001
        arucoParams.adaptiveThreshWinSizeStep = 1
        arucoParams.adaptiveThreshWinSizeMin = 3
        arucoParams.adaptiveThreshWinSizeMax = 32
    if 1==1:
        f=18
        arucoParams.minMarkerPerimeterRate = 1/(1<<f)
        arucoParams.cornerRefinementWinSize = 1
        arucoParams.cornerRefinementMinAccuracy = 1/16
        arucoParams.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
        #arucoParams.minMarkerDistanceRate = 1/(1<<f)

    (corners, ids, rejected) = cv2.aruco.detectMarkers(
        img, aruco_dict, parameters=arucoParams)

    if ids is None:
        print("no markers found")
        return
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
            col=mcolor.get(_id)
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
            col=mcolor.get(i)
            cv2.circle(sheet_debug, p, radius=3, color=col, thickness=9)
            #print(f'i is {i}, color is {colors[i]}')
    return barcode


def rectify_image(sheet, markers):
    print(f"rectifying image, {sheet.shape=}")
    dbg1 = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

    markers = markers[0]
    assert(len(markers) == 4)

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

    if tmp[2][0] < tmp[3][0]:
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
            col=mcolor.get(i)
            cv2.circle(dbg1, j, radius=3, color=col, thickness=9)
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
    begin   = sorted(markers, key=lambda x: x[1])
    print(f"qrange markers: {begin}")

    ret=[]
    for i in range(len(begin)-1):
        ret.append({"yfrom": begin[i][1], 'yto': begin[i+1][1]})

    ret.append({"yfrom": begin[-1][1], 'yto': sheet.shape[0]})

    return ret


save_debug_number=0
def save_debug(img, what):
    global save_debug_number
    cv2.imwrite("debug/" + str(save_debug_number) + "-" + what + ".png", img)
    save_debug_number += 1

    
def draw_markers(img, markers):
    a=img.copy()
    if markers is None:
        print("no markers to draw")
        return
    for i,j in markers.items():
        for k in j:
            col=mcolor.get(i)
            cv2.circle(a, k, radius=5, color=col, thickness=3)
    return a

if __name__ == '__main__':

    sheet_f = "scans/./200dpi/-000.ppm"
    sheet_f = "process/t.tiff"
    try:
        sheet_f = sys.argv[1]
    except IndexError:
        pass
        

    _sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)
    save_debug(_sheet, "original")
    sheet = _sheet.copy()
    barcode = get_barcode(sheet)
    markers = get_markers(sheet)



    if len(markers[0]) == 4:
        sheet = rectify_image(sheet, markers)
        save_debug(sheet, "rectified")
        markers = get_markers(sheet)
    else:
        print(f"WARN: {len(markers[0])} 0markers found; != 4; can't rectfiy image; continuing with unrectified image")

    _, _bw_master = cv2.threshold(
        cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB),
        192, 255, cv2.THRESH_BINARY
        )
    _bw_master = cv2.cvtColor(_bw_master,cv2.COLOR_RGB2GRAY)
    save_debug(_bw_master, "bw")

    bw_master = _bw_master.copy()
    #bw_master = bw_master * -1
    ex_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
    bw_master = bw_master * -1
    bw_master = cv2.dilate(bw_master, ex_kernel, iterations=2)
    bw_master = bw_master * -1
    save_debug(bw_master, "bw-dilate")

    #bw_master = cv2.morphologyEx(bw_master, cv2.MORPH_CLOSE,(3,3),)
    ##bw_master = bw_master * -1
    #save_debug(bw_master, "bw-close")

    sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

    for i,j in markers.items():
        col=mcolor.get(i)
        for k in j:
            cv2.circle(sheet_debug, k, radius=6, color=col, thickness=4)

    qranges = get_question_ranges(sheet, markers[2])


    if 1==1:
        col = mcolor.get(1)
        c_checked = mcolor.get(6)
        c_unchecked = mcolor.get(7)
            
        for j,i in enumerate(qranges):
            sd = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)
            #sd2 = cv2.cvtColor(bw_master,cv2.COLOR_GRAY2RGB)
            #sd2 = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)
            sd2 = bw_master.copy()
            print(sd2.shape)
            sd2 = np.uint8(sd2)
            print(sd2.shape)
            #sd2 = sd2 * -1
            sd2 = cv2.cvtColor(sd2,cv2.COLOR_GRAY2RGB)

            (yfrom, yto) = (i['yfrom'], i['yto'])

            print(f'all cols: {markers[1]}')
            print('=======================================')
            print(f'question {j} range {yfrom} <= y <= {yto}')
            lines = list(filter(lambda x: x[1] >= yfrom+1 and x[1] <= yto+10, markers[4]))
            print(f'{lines=}')
            cols =  list(filter(lambda x: x[1] >= yfrom+1 and x[1] <= yto+10, markers[1]))
            print(f'{cols=}')
            print('=======================================')
            square = 20

            color=mcolor.get(4)
            print(f'{lines=}')
            for i in lines:
                cv2.circle(sd2, i, radius=square//2, color=color, thickness=2)

            color=mcolor.get(1)
            print(f'{cols=}')
            for i in cols:
                cv2.circle(sd2, i, radius=square//2, color=color, thickness=2)

            for l in lines:
                for c in cols:
                    p=(c[0], l[1])
                    print(f'checking {p} for mark')
                    tmp = _bw_master[
                        int(p[1]+square/-2):int(p[1]+square/2),
                        int(p[0]+square/-2):int(p[0]+square/2),
                    ]
                    tmp[tmp > 0] = 1

                    avg = np.average(tmp)
                    print(f'********************')
                    print(tmp)
                    print(avg)
                    print(f'********************')
                    checked=False
                    print(f'avg gray value @ {p} = {avg}')
                    if avg < 180:
                        checked=True

                    cc=c_unchecked
                    str2 = "U"
                    rad=4
                    if checked:
                        rad=9
                        cc=c_checked
                        str2 = "C"
                    shift_right=400

                    cc2=mcolor.get(1)
                    cv2.circle(sd2, (p[0], p[1]),
                        radius=square//2, color=cc2, thickness=3
                    )

                    cv2.circle(sd2, (p[0]+shift_right, p[1]),
                        radius=rad, color=cc, thickness=2
                    )
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    #cv2.putText(sd2, f'{str2}{avg}', (p[0]+shift_right, p[1]), font, 1, 0)
                    cv2.putText(sd2, f'{avg}', (p[0]+shift_right*2, p[1]), font, 1, 0)
            save_debug(sd2, f"qrange-{j}")

    save_debug(sheet_debug, "markers")
    cv2.imwrite("debug/sheet.png", sheet_debug)
