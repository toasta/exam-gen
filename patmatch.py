import cv2
import numpy as np

marker3_f="common/marker2tiff/m3.tiff"

sheet_f = "process/t.tiff"


_markers  = [3,4,5,6]

colors = [None for i in range(max(_markers)+1)]
colors[3] = (255,0,0)
colors[4] = (0, 255,0)
colors[5] = (0, 0, 255)
colors[6] = (255, 255,0)



marker = [None for i in range(max(_markers)+1)]
for i in _markers:
    print(f'{i=}')
    marker[i] = cv2.imread(f'common/marker2tiff/m{i}.tiff', cv2.IMREAD_GRAYSCALE)

sheet = cv2.imread(sheet_f, cv2.IMREAD_GRAYSCALE)

sheet_debug = cv2.cvtColor(sheet,cv2.COLOR_GRAY2RGB)

def match_template(img, marker, threshold):
    res = cv2.matchTemplate(img, marker, method=cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > threshold)
    return loc


matches = [None for i in range(max(_markers)+1)]
for i in _markers:
    t=match_template(sheet, marker[i], .7)
    print(f'{t=}')
    matches[i] = t


for j in _markers:
    _marker= marker[j]
    _match = matches[j]
    nmatch = len(_match[0])
    print(f'{nmatch=} matches for marker {j}')
    for i in range(nmatch):
        (x, y) = _match[1][i], _match[0][i]
        mshalfx = _marker.shape[1]//2
        mshalfy = _marker.shape[0]//2
        pos=(x + mshalfx, y + mshalfy)
        print(f"Draw {pos=}")
        cv2.circle(sheet_debug, pos, radius=1, color=colors[j], thickness=5)

cv2.imwrite("sheet_debug.png", sheet_debug)
