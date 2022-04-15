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
    for j in ['begin', 'end']: 
            i='row'
            for k in range(int(CFG[SECTION]['num_rows'])):
                ss = f'{i}.{j}.{k}'
                fn = f'out/{co}.png'
                o = {
                    'what': i,
                    'beginend': j,
                    'row': k,
                    'filename': fn,
                    'ss': ss,
                }
                short2object[ss] = o
                id2object[co] = o
                co += 1
            i='line'
            for k in range(int(CFG[SECTION]['num_lines'])):
                for r in range(int(CFG[SECTION]['NUM_REPEATS'])):
                    fn = f'out/{co}.png'
                    ss = f'{i}.{j}.{k}.{r}'
                    o = {
                        'what': i,
                        'beginend': j,
                        'line': k,
                        'repeat': r,
                        'filename': fn,
                        'ss': ss,
                    }
                    short2object[ss] = o
                    id2object[co] = o
                    co += 1

    #r= mapt.generate('tag25h9', range(co))
    r= mapt.generate('tag36h11', range(co))
    for i,j in enumerate(r):
        fn = 'out/' + str(i) + '.png'
        #j = np.repeat(np.repeat(j, scale, axis=0), scale, axis=1)
        img = Image.fromarray(j.array*255)
        img.save(fn, "PNG", mode="1")
    with open('markers.json', "w") as fh:
        json.dump({
            'short2object': short2object,
            'id2object': id2object,
        }, fh)

if __name__ == "__main__":
    gen_common()
