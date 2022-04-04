#! /usr/bin/env python3

import apriltag
import cv2
import sys
img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
det = apriltag.Detector()
res = det.detect(img)

print(res)
