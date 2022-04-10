import cv2
import numpy as np

marker1_f="m1.tiff"
marker2_f="m2.tiff"

sheet_f = "test.png"


marker1 = cv2.imread(marker1_f, cv2.IMREAD_GRAYSCALE)
marker2 = cv2.imread(marker2_f, cv2.IMREAD_GRAYSCALE)
sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)

sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

def match_template(img, marker, threshold):
    res = cv2.matchTemplate(img, marker, method=cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > threshold)
    return loc


m1 = match_template(sheet, marker1, .7)
m2 = match_template(sheet, marker2, .7)

for i in range(len(m1[0])):
    pos=(m1[1][i] + marker1.shape[0]//2, m1[0][i] + marker1.shape[1]//2)
    print(f"Draw {pos=}")
    cv2.circle(sheet_debug, pos, radius=1, color=(255,0,0), thickness=5)

for i in range(len(m2[0])):
    pos=(m2[1][i] + marker2.shape[0]//2, m2[0][i] + marker1.shape[1]//2)
    print(f"Draw {pos=}")
    cv2.circle(sheet_debug, pos, radius=1, color=(0,255,0), thickness=5)

cv2.imwrite("sheet_debug.png", sheet_debug)
