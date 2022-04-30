#! /bin/bash

set -x 

convert -density 300 out/a.pdf[0] \
    -background white -alpha remove \
    -rotate -3 \
    process/t.tiff
#   -blur 2x2 \
#    +noise poisson \
