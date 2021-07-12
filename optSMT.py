import hashlib

def blake2b(nbyte=32):
    def f(x):
        return hashlib.blake2b(x, digest_size=nbyte).digest()
    return f


def bytes_to_int(x):
    return int.from_bytes(x, "big")


def int_to_bytes(x, byte=32):
    return x.to_bytes(byte, "big")


class optSMT(object):
  
    def __init__(self, hash_bytes=32, db=None):
        self.db = db
        self.HASH_BYTES = hash_bytes
        self.HASH_BITS = hash_bytes << 3
        self.hash = blake2b(hash_bytes)
        self.nil = b"" * hash_bytes
        self.nilproof = [self.nil] #Cache list

    def smtree(self):
        h = self.nil
        for _ in range(self.HASH_BITS):
            hh = h + h
            h = self.hash(hh)
            self.nilproof.insert(0, h) #insert latest value(parent hash) at beginning of list,root at begin
            self.db.put(h, hh)
        return h


    def siblings(self, root, key):
        nshift = self.HASH_BITS - 1 #255
        bits = bytes_to_int(key)
        h = root
        proof = []
        for i in range(self.HASH_BITS):
            if h == self.nilproof[i]: #if hash is already available in cache return the proof
                return proof
            hh = self.db.get(h)
            if (bits >> nshift) & 1:
                h = hh[self.HASH_BYTES :]
                proof.append(hh[: self.HASH_BYTES])
            else:
                h = hh[: self.HASH_BYTES]
                proof.append(hh[self.HASH_BYTES :])
            bits <<= 1
        return proof

    def update(self, root, key, leaf):
        proof = self.siblings(root, key)
        iNIL = len(proof) #len of proof list
        bits = bytes_to_int(key)
        h = leaf
        for i in reversed(range(self.HASH_BITS)): #from last bit
            if i < iNIL: #if length is less than proof length
                pf = proof[i]
            else:
                pf = self.nilproof[i + 1] #if length exceeds proof legnth, we take value from cache
            if bits & 1:
                hh = pf + h
            else:
                hh = h + pf
            h = self.hash(hh)
            self.db.put(h, hh)
            bits >>= 1
        return h















