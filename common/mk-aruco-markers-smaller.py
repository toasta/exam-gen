import re
import subprocess
import sys
import numpy as np
import cv2.aruco
import cv2


# 5 markers is the lowest for size 3
num_markers = 5
size=3
border_bits = 1
imsize = size + 2*border_bits
imsize = (imsize, imsize)

a=cv2.aruco.Dictionary_create(num_markers, size)
#print(a.bytesList)

fh = open('mydict.dict', 'w')
buf = []
buf.append(f'nmarkers: {num_markers}')
buf.append(f'markersize: {size}')
buf.append(f'maxCorrectionBits: {a.maxCorrectionBits}')
for i,j in enumerate(cv2.aruco.Dictionary_getBitsFromByteList(a.bytesList, size*size)):
    b=str(j)
    b = re.sub('[^01]', '', b)
    buf.append(f'marker_{i}: "{b}"')

#cvf = cv2.FileStorage("mydict.dict", cv2.FILE_STORAGE_WRITE)
#cvf.write("D", "\n".join(buf))

np.savez("cd.npz", nmarkers=num_markers,
    markersize=size,
    maxCorrectionBits=a.maxCorrectionBits,
    bytesList=a.bytesList,
    )

sscale=10000

def empty_and_checked():
    imsize=(5*2,5*2)
    sscale=1000
    tag = np.ones(imsize, dtype="uint8")
    tag[tag > 0] = 255
    to=imsize[0]-1
    for i in range(0, to):
        tag[i][0] = 0
        tag[i][to] = 0
        tag[to][i] = 0
        tag[0][i] = 0
    tag[to][to] = 0

    i="pos_empty"
    of1=f'out/orig_{i}.png'
    of2=f'out/{sscale}_{i}.png'
    of3=f'out/{i}.png'
    cv2.imwrite(of1, tag)
    subprocess.run(['convert', of1, 
             '-background', 'white',
             '-bordercolor', 'white',
             '-border', '1',
            of3])
    subprocess.run(['convert', of1, '-scale', str(sscale) + "%", of2])

    for i in range(1, to):
        tag[i][i] = 0
        tag[to-i][i] = 0

    i="pos_checked"
    of1=f'out/orig_{i}.png'
    of2=f'out/{sscale}_{i}.png'
    of3=f'out/{i}.png'
    cv2.imwrite(of1, tag)
    subprocess.run(['convert', of1, 
             '-background', 'white',
             '-bordercolor', 'white',
             '-border', '1',
            of3])
    subprocess.run(['convert', of1, '-scale', str(sscale) + "%", of2])


empty_and_checked()

for i in range(num_markers):
    tag = np.zeros(imsize, dtype="uint8")
    # dict, id, sidePixel, img, border
    cv2.aruco.drawMarker(a, i, imsize[0], tag, border_bits)
    of1=f'out/orig_{i}.png'
    of2=f'out/1000_{i}.png'
    of3=f'out/{i}.png'
    cv2.imwrite(of1, tag)
    subprocess.run(['convert', of1, 
         '-background', 'white',
         '-bordercolor', 'white',
         '-border', '1',
        of3])
    subprocess.run(['convert', of1, '-scale', '1000%', of2])

