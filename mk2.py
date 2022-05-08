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
import base64

import mprotos.main_pb2 as main_pb2
import qrcode

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
    # python/zbar is so broken w/ binary data; encoding works fine;
    # but none can decode it. using the fork with the exposed
    # binary=True flag doesnt even decode anything.
    iv = get_iv()
    zipped = lzma.compress(json.dumps(obj).encode('utf8'))

    o = main_pb2.mainData()

    o.iv = iv
    o.init = init

    cmd=["openssl", "enc", "-chacha20", "-iv", iv.hex(), "-nosalt", "-K", key.hex()]
    res=subprocess.run(cmd, capture_output=True, input=zipped)
    o.data = res.stdout

    oo2 = o.SerializeToString()
    ddata = base64.b85encode(oo2)

    qr = qrcode.QRCode( 
        box_size = 1,
        border=2,
        version=None
    )

    qr.add_data(ddata)
    qr.make(fit=True)

    im = qr.make_image()
    im.save(of)


    return True

def gen_one_question_block(i, key=None):

    points = i.get('points', 1)
    tmp_latex = {
        'q': i['q'],
        'points': points,
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
