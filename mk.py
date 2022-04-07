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
    data['question_order'] = []
    data['answers'] = {}

    qlatex = []
    #random.seed(43123)
    scard = []
    for i in random.sample(q, len(q)):
        tmp_latex = {}
        tmp_latex['question'] = i['q']
        tmp_latex['answers'] = []

        tmp_score = {'question': '', 'answers': [] }
        tmp_score['question'] = i['id']

        nanswers = len(i['a'])
        if nanswers > max_answers:
            max_answers  = nanswers

        for j in i['a']:
            tmp_score['answers'].append(j['sol'])
            tmp_latex['answers'].append(j['ap'])

        scard.append(tmp_score)
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
        'max_answers4latex': " ".join(['| l ' for i in range(max_answers)]),
    }
    rscore['card'] = scard

    tmpl = env.get_template(CFG[SECTION]['TEMPLATE'])
    print(json.dumps(rscore, indent=1), file=sys.stderr)
    print(tmpl.render(qlatex=qlatex, score=rscore, cfg=CFG[SECTION], short2object=short2object['short2object']))


if __name__ == "__main__":
    with open("markers.json") as fh:
        short2object = json.load(fh)
    doit()
