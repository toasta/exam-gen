#! /bin/bash

set -x 

convert -density 300 out/a.pdf[0] \
    -background white -alpha remove \
    process/t.tiff
#   -blur 2x2 \
#    -rotate -3 \
#    +noise poisson \
