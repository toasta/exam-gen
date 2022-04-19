import cv2.aruco
import re
import cv2
import numpy as np
import subprocess


num_markers = 5
size=3
imsize = (10,10)

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

cvf = cv2.FileStorage("mydict.dict", cv2.FILE_STORAGE_WRITE)

cvf.write("D", "\n".join(buf))


for i in range(num_markers):
    tag = np.zeros(imsize, dtype="uint8")
    # dict, id, sidePixel, img, border
    cv2.aruco.drawMarker(a, i, imsize[0], tag, 1)
    of1=f'out/{i}.png'
    of2=f'out/1000_{i}.png'
    cv2.imwrite(f"out/{i}.png", tag)
    subprocess.run(['convert', of1, '-scale', '1000%', of2])
