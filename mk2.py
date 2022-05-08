#! /usr/bin/env python3

import random
import secrets
import jinja2
import json
import hashlib
import subprocess
import os
import sys
import struct
import lzma

from common import get_key

import configparser

CFG = configparser.ConfigParser()
CFG.read('secrets.ini')
SECTION="DEFAULT"
PKEY_KEY = bytes.fromhex(CFG[SECTION]['PKEY_KEY'])

CFG = configparser.ConfigParser()
CFG.read('config.ini')
SECTION="DEFAULT"

INIT_LEN_BYTES = int(CFG[SECTION]['INIT_LEN_BYTES'])


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['./templates/'])
)
env.filters['jsonify'] = json.dumps



q=json.load(open('questions.json'))

ret = []


TMPD='/dev/shm/tmp1/'
os.makedirs(TMPD, exist_ok=True)

def grh(b):
    c = secrets.token_bytes(b)
    return c

def get_iv():
    h = secrets.token_bytes(int(CFG[SECTION]['IV_LEN_BITS'])//8)
    return h


def jsonify_encrypt_qrcode(obj=None, key=None, of=None, init=None):
    iv = get_iv()
    _a = json.dumps(obj)
    a = _a.encode('utf8')

    print(f"qrcode: {iv=}, {key=}, {init=}")
    print(f"qrcode: {iv.hex()=}, {key.hex()=}, {init.hex()=}")

    # compressing before encryption unsafe?
    # compressing crypted does not make sense, should be fullu random // full entropy
    #
    o2 = {}

    options = 0

    zipped = lzma.compress(a)

    if len(zipped) < len(a):
        print(f"lzma size {len(zipped)} < {len(a)}, using compressed form; {len(zipped)/len(a):.2f}")
        options = options | (1 << 0)
        a = zipped

    cmd=["openssl", "enc", "-chacha20", "-iv", iv.hex(), "-nosalt", "-K", key.hex()]
    res=subprocess.run(cmd, capture_output=True, input=a)
    crypted=res.stdout

    o2['iv'] = iv
    o2['options'] = options.to_bytes(1, byteorder='big')
    o2['init'] = init
    o2['c'] = crypted

    cmd=['qrencode', 
        '--type', 'png',
        '--output', of,
        '--dpi', '600',
        '--size', '1',
        '--margin', '4',
        '--8bit',
        ]
    r = subprocess.run(cmd, input=json.dumps(o2), capture_output=True, check=True)
    print(r)
    return True

def gen_one_question_block(i, key=None):

    points = i.get('points', 1)
    tmp_latex = {
        'q': i['q'],
        'points': points,
        'qr': None,
        'a': []
    }

    tscore = []
    for j in random.sample(i['a'], len(i['a'])):
        tmp_latex['a'].append(j['ap'])

        factor = j.get('factor', 1)
        nofalse = j.get('nofalse', False)
        points_checked = 0
        points_unchecked = 0

        # FIXME -- something wrong w/ points_unchecked
        if j.get('sol', False) == True:
            points_checked      = (factor * +1)
            points_unchecked    = 0
            if not nofalse:
                points_unchecked = 0
        else:
            points_checked      = (factor * -1)
            points_unchecked    = 0
            if not nofalse:
                points_unchecked = 0

        tscore.append([points_checked, points_unchecked])

    tmp_latex['solution'] = tscore

    return tmp_latex


def doit():



    max_answers = -1
    for i in q:
        nanswers = len(i['a'])
        if nanswers > max_answers:
            max_answers  = nanswers


    basics = {}

    names = ["Selabin Deresch", "Testos Teron"]
    names = ["Selabin Deresch"]

    all_sheets = []


    for name in names:
        init=grh(INIT_LEN_BYTES)
        key=get_key(init, PKEY_KEY)

        this_sheet = {}
        this_sheet['name'] = name
        this_sheet['qr'] = None
        this_sheet['questions'] = []

        
        for j, i in enumerate(random.sample(q, len(q))):
            tmp = gen_one_question_block(i, key=key)
            this_sheet['questions'].append(tmp)



        of2 = f'out/bc.png'

        jsonify_encrypt_qrcode(obj=this_sheet, key=key, of=of2, init=init)
        this_sheet['qr'] = of2
        _a = json.dumps(this_sheet, indent=1)
        this_sheet['json_readable'] = _a

        all_sheets.append(this_sheet)

    common = {}
    common['marker_width'] = CFG[SECTION]['MARKER_WIDTH']
    common['main_qr_width'] = CFG[SECTION]['MAIN_QR_WIDTH']


    tmpl = env.get_template(CFG[SECTION]['TEMPLATE'])
    with open("a.tex", "w") as fh:
        print(tmpl.render(
            all_sheets=all_sheets, 
            cfg=CFG[SECTION], 
            #short2object=short2object['short2object'],
            common=common,
            ),
            file=fh
            )


if __name__ == "__main__":
    #mfile="markers-simple.json"
    #with open(mfile) as fh:
    #    short2object = json.load(fh)
    doit()
