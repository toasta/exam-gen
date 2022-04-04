#! /usr/bin/env python3


import numpy as np
import pyboof as pb
import sys

det_qr = pb.FactoryFiducial(np.uint8).qrcode()
det_mqr = pb.FactoryFiducial(np.uint8).microqr()

print(f'loading {sys.argv[1]}')
img = pb.load_single_band(sys.argv[1], np.uint8)
print(img)


det_qr.detect(img)

print(f'got {len(det_qr.detections)} codes')
for i in det_qr.detections:
    print(str(i.bounds))

#pb.swing.show_list([(img, 'img')])

#input("F")

##for i in [det_mqr, det_qr]:
#for i in [det_mqr]:
#    i.detect(img)
#    print(i.detections)
#    for j in i.detections:
#        print(str(j.bounds))
#
