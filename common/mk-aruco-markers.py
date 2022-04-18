import cv2.aruco
import cv2
import numpy as np



DT=cv2.aruco.DICT_4X4_50

arudict = cv2.aruco.Dictionary_get(DT)

size=16
for i in range(4):
    
    tag = np.zeros((size,size,1), dtype="uint8")
    cv2.aruco.drawMarker(arudict, i, size, tag, 1)
    cv2.imwrite(f"out/{i}.png", tag)
