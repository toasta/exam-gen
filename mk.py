#! /usr/bin/env python3

import random
import jinja2
import json
import hashlib
import subprocess
import os
import sys
import struct

import configparser


CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['./templates/'])
)
env.filters['jsonify'] = json.dumps


def genqr(content, outfile, micro=False, micro_version=3):
    if os.path.exists(outfile):
        return
    cmd=['qrencode', 
        '-t', 'png',
        '-o', outfile,
        '-d', '600',
        ]
    if micro:
        cmd.extend(["-M", "-v", str(micro_version)])
    cmd.append(content)
    #print(json.dumps(cmd))
    subprocess.run(cmd)

    tag2id = {}

q=json.load(open('questions.json'))

ret = []


PKEY_KEY = bytes.fromhex('135762ba0049cf6727b211732fdfaf202718762539d1e115dda0abeb2ab71792')
PKEY_IV  = bytes.fromhex('7b24501c646dc54f0655f11019da68786dcc8a257faf057842d869073ce8c4d6')

TMPD='/dev/shm/tmp1/'
os.makedirs(TMPD, exist_ok=True)

def grh(b):
    #TODO use os.random or secrets
    fh = open('/dev/urandom', 'rb')
    c = fh.read(b)
    return c

def get_key(b):
    h = hashlib.blake2b(b, key=PKEY_KEY, digest_size=256//8).hexdigest()
    return h

def get_iv(b):
    h = hashlib.blake2b(b, key=PKEY_IV, digest_size=96//8).hexdigest()
    return h


def doit():

    max_answers = -1
    init=grh(16)
    key=get_key(init)
    iv=get_iv(init)
    qco = 0

    data = {}
    data['answers'] = {}

    qlatex = []
    #random.seed(43123)
    scard = []
    for j, i in enumerate(random.sample(q, len(q))):

        points = i.get('points', 1)

        tmp_latex = {
            'q': i['q'],
            'points': points,
            'a': []
        }
        nanswers = len(i['a'])
        if nanswers > max_answers:
            max_answers  = nanswers

        tscore = []
        for j in random.sample(i['a'], len(i['a'])):
            tmp_latex['a'].append(j['ap'])

            factor = i.get('factor', 1)
            nofalse = i.get('nofalse')
            points_checked = 0
            points_unchecked = 0

            if j['sol'] == True:
                points_checked = (factor * 1)
                points_unchecked = (factor * -1)
                if not nofalse:
                    points_unchecked = 0

            if j['sol'] == False:
                points_checked = (factor * -1)
                points_unchecked = (factor * 1)
                if not nofalse:
                    points_unchecked = 0

            tscore.append([points_checked, points_unchecked])

        scard.append(tscore)
        qlatex.append(tmp_latex)


    cmd=["openssl", "enc", "-chacha20", "-iv", iv, "-nosalt", "-K", key]
    a = json.dumps(scard)
    crypted=subprocess.run(cmd, capture_output=True, input=a.encode('utf8')).stdout
    of='/dev/shm/a.png'

    cmd=['qrencode', 
        '-t', 'png',
        '-o', of,
        '-d', '600',
        '--8bit',
        ]
    subprocess.run(cmd, input=crypted).stdout
    rscore = {}
    rscore['basics'] = {
        'qr': of,
        'max_answers': max_answers,
    }
    rscore['card'] = scard

    tmpl = env.get_template(CFG[SECTION]['TEMPLATE'])
    print(json.dumps(qlatex), file=sys.stderr)
    print(json.dumps(rscore), file=sys.stderr)
    print(tmpl.render(qlatex=qlatex, score=rscore, cfg=CFG[SECTION], short2object=short2object['short2object']))


if __name__ == "__main__":
    mfile="markers-simple.json"
    with open(mfile) as fh:
        short2object = json.load(fh)
    doit()
