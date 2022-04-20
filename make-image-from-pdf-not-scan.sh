#! /bin/bash

set -x 

convert -density 200 out/a.pdf \
    -background white -alpha remove \
    -rotate 2 \
    process/t.tiff
