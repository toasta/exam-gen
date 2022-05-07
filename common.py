import hashlib

def get_key(b, key):
    h = hashlib.blake2b(b, key=key, digest_size=256//8).digest()
    return h

