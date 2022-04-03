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

def genqr(content, outfile):
    if os.path.exists(outfile):
        return
    cmd=['qrencode', 
        '-t', 'png',
        '-o', outfile,
        '-d', '600',
        content,
        ]
    subprocess.run(cmd)

def gen_common_qrs():
    # line row
    for i in ['l','r']:
        # begin end
        for j in ['b', 'e']: 
            for k in range(int(CFG[SECTION]['num_lines'])):
                for r in range(int(CFG[SECTION]['NUM_REPEATS'])):
                    ss = f'{i}.{j}.{k}.{r}.png'
                    genqr(ss, CFG[SECTION]['static_qr_dir'] + "/" + ss + ".png")
            for k in range(int(CFG[SECTION]['num_rows'])):
                ss = f'{i}.{j}.{k}.png'
                genqr(ss, CFG[SECTION]['static_qr_dir'] + "/" + ss + ".png")

q=[
    {
        'id': '7664151f02cd78499b4780e68ea1098a',
        'q': 'Welche Hashfunktionen gelten als unsicher?',
        'a': [
            { 'ap': 'sha1', 'sol': True },
            #{ 'ap': 'md5', 'sol': True },
            #{ 'ap': 'blake2b', 'sol': False },
            { 'ap': 'sha2', 'sol': False },
        ]
    },
    {
        'id': '3ae54f9257bb8c6b8caa2c1094d940c8',
        'q': 'Wofuer steht SFP?',
        'a': [
            { 'ap': 'Small formfaktor pluggable', 'sol': True },
            { 'ap': 'Super fine phase', 'sol': False },
            { 'ap': 'signal faktor phase', 'sol': False },
            { 'ap': 'signal format plug', 'sol': False },
        ]
    }
]
ret = []


PKEY_KEY = bytes.fromhex('135762ba0049cf6727b211732fdfaf202718762539d1e115dda0abeb2ab71792')
PKEY_IV  = bytes.fromhex('7b24501c646dc54f0655f11019da68786dcc8a257faf057842d869073ce8c4d6')

TMPD='/dev/shm/tmp1/'
os.makedirs(TMPD, exist_ok=True)

def grh(b):
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
    random.seed(43123)
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

    tmpl = env.get_template('t.tex')
    print(json.dumps(rscore, indent=1), file=sys.stderr)
    print(tmpl.render(qlatex=qlatex, score=rscore, cfg=CFG[SECTION]))


if __name__ == "__main__":
    gen_common_qrs()
    doit()
