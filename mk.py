#! /usr/bin/env python3

import random
import jinja2
import json
import hashlib
import subprocess
import os
import struct

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['./templates/'])
)


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


qco = 0
for i in random.sample(q, len(q)):
    qco += 1
    q = i['q']
    init=grh(16)
    key=get_key(init)
    iv=get_iv(init)
    a=init + bytes.fromhex(i['id'])

    of=TMPD + grh(16).hex() + ".png"


    o = {}
    o['q'] = q
    o['a'] = []
    o['qco'] = qco
    answers = random.sample(i['a'], len(i['a']))
    cor=[]
    cor=0
    co=0
    for j in answers:
        if j['sol']:
            cor |= (1<<co)
        o['a'].append(j['ap'])
        co += 1


    a=bytes.fromhex(i['id']) + struct.pack("!L", cor)
    cmd=["openssl", "enc", "-chacha20", "-iv", iv, "-nosalt", "-K", key]
    a=subprocess.run(cmd, capture_output=True, input=a).stdout

    b = init + a
    cmd=['qrencode', 
        '-t', 'png',
        '-o', of,
        '-d', '600',
        '--8bit',
        ]
        #'-l', 'L',
    subprocess.run(cmd, input=a).stdout
    o['qr'] = r'\includegraphics[width=2cm]{' + of + '}'
    ret.append(o)



tmpl = env.get_template('t.tex')
print(tmpl.render(ret=ret))




    
