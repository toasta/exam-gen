#! /bin/bash

DEN=600

convert -density $DEN marker1.pdf[0] -trim -border 1x1 m1.tiff
convert -density $DEN marker1.pdf[1] -trim -border 1x1 m2.tiff
