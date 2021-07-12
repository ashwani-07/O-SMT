import hashlib

def bytes_to_int(x):
    return int.from_bytes(x, "big") #big because we need msb at beginning of bit array


def blake2b(nbyte=32):
    def f(x):
        return hashlib.blake2b(x, digest_size=nbyte).digest()
    return f

class SMT(object):
    def __init__(self, hash_bytes=32, db=None): #Initialise tree
        self.db = db #database for storing hashes
        self.HASH_BYTES = hash_bytes #32
        self.HASH_BITS = hash_bytes << 3 #256
        self.hash = blake2b(hash_bytes) #hash fun. based on blake2b
        self.nil = b"" * hash_bytes #Default hash

    def smtree(self):
        h = self.nil #Dafault leaf hash
        for _ in range(self.HASH_BITS): #Start from leaf and go up to root to fill deafual hash
            hh = h + h
            h = self.hash(hh)
            self.db.put(h, hh) # Save parent hash as key and child concat. as value
        return h

    def siblings(self, root, key):
        bits = bytes_to_int(key) #For retrieval
        nshift = self.HASH_BITS - 1 #255
        h = root
        proof = [] #This array contains the sibling to calcluate hash on the way
        for _ in range(self.HASH_BITS):
            hh = self.db.get(h) #get value from database
            if (bits >> nshift) & 1: #checking if it's a right child
                h = hh[self.HASH_BYTES :] #Iterate for right child
                proof.append(hh[: self.HASH_BYTES]) #Add left child to proof
            else: #checking if it's a left child
                h = hh[: self.HASH_BYTES] #Iterate for left child
                proof.append(hh[self.HASH_BYTES :]) #Add right child to proof
            bits <<= 1 #Check next bit from MSB
        return proof

    def update(self, root, key, leaf):
        proof = self.siblings(root, key) #Get siblings of key
        bits = bytes_to_int(key)
        h = leaf
        #Take value from end as it contains sibling of leaf
        for i in range(self.HASH_BITS):
            if bits & 1: #check lsb, if right child
                hh = proof[-1 - i] + h #concat proof as left child
            else:
                hh = h + proof[-1 - i] #concat proof as right child
            h = self.hash(hh)
            self.db.put(h, hh) #Finally we put new hashes in database
            bits >>= 1
        return h
        