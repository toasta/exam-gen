#! /usr/bin/env python3

import os
import sys
import json

import configparser
import moms_apriltag as mapt
from PIL import  Image
import numpy as np



CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"

def gen_common():
    # line row
    co = 0
    short2object = {}
    id2object = {}
    # smallest (?) tag 16h5 supports 00..29
    
    repeat=30//2
    for k in range( repeat ):
            ss = f'col.{k}'
            o = {
                'ss': ss,
                'val': k,
                'what': 'col',
                'fn': 'out/short-' + str(co) + '.png'
            }
            short2object[ss] = o
            id2object[co] = o
            co += 1

    for k in range(repeat):
            ss = f'row.{k}'
            o = {
                'what': 'row',
                'val': k,
                'ss': ss,
                'fn': 'out/short-' + str(co) + '.png'
            }
            short2object[ss] = o
            id2object[co] = o
            co += 1

    #r= mapt.generate('tag25h9', range(co))
    r= mapt.generate('tag16h5', range(29))
    for i,j in enumerate(r):
        fn = 'out/short-' + str(i) + '.png'
        #j = np.repeat(np.repeat(j, scale, axis=0), scale, axis=1)
        img = Image.fromarray(j.array*255)
        img.save(fn, "PNG", mode="1")
    with open('markers-simple.json', "w") as fh:
        json.dump({
            'short2object': short2object,
            'id2object': id2object,
        }, fh)

if __name__ == "__main__":
    gen_common()
