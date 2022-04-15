#! /bin/bash

set -x 

convert -density 300 out/a.pdf -background white -alpha remove process/t.tiff
