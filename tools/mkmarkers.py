#! /usr/bin/env python3

import sys
import json
from PIL import Image, ImageDraw, ImageColor, ImageOps
import aggdraw

w=256

im1 = Image.new('L', (w,w), color=255)

draw = ImageDraw.Draw(im1)

for i in range(10):
    draw.regular_polygon((w/2, w/2, w/2-i), n_sides=6)
    draw.regular_polygon((w/2, w/2, w/2/2-i), n_sides=3)
im1.save("mm2.png")


