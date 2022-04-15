#! /bin/bash

set -x 

convert -density 200 out/a.pdf \
    -background white -alpha remove \
    -rotate 1 \
    process/t.tiff
