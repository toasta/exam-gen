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

q=[
    {
        'id': '7664151f02cd78499b4780e68ea1098a',
        'q': 'Welche Hashfunktionen gelten als unsicher?',
        'a': [
            { 'ap': 'sha1', 'sol': True },
            { 'ap': 'md5', 'sol': True },
            { 'ap': 'blake2b', 'sol': False },
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
    },
    {
        'id': 'b20de167d27764cc6f423d2ec6d0098a',
        'q': 'Wieviele IPV4 Adressen gibt es?',
        'a': [
            { 'ap': '$2^{24}$', 'sol': False },
            { 'ap': '$2^{32}$', 'sol': True },
            { 'ap': '$2^{8}$', 'sol': False },
            { 'ap': '$2^{16}$', 'sol': False },
            { 'ap': '$2^{64}$', 'sol': False },
        ]
    },
    {
        'id': 'f24d45a19819f8551c155cf7db5408d8',
        'q': 'Wieviele IPV6 Adressen gibt es?',
        'a': [
            { 'ap': '$2^{64}$', 'sol': False },
            { 'ap': '$2^{60}$', 'sol': False },
            { 'ap': '$2^{6}$', 'sol': False },
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

    tmpl = env.get_template('t.tex')
    print(json.dumps(rscore, indent=1), file=sys.stderr)
    print(tmpl.render(qlatex=qlatex, score=rscore, cfg=CFG[SECTION], short2object=short2object['short2object']))


if __name__ == "__main__":
    with open("markers.json") as fh:
        short2object = json.load(fh)
    doit()
