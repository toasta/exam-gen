#! /bin/bash

set -x 

convert -density 300 out/a.pdf \
    -background white -alpha remove \
    -rotate -3 \
    -blur 2x2 \
    process/t.tiff
#    +noise poisson \
