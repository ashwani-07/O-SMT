import os
import hashlib
from functools import wraps
from time import time
from database import Database
from optSMT import optSMT
from SMT import SMT


def blake2b(nbyte=32):
    def f(x):
        return hashlib.blake2b(x, digest_size=nbyte).digest()
    return f

def gen_keys(size, hash_fn=blake2b(32), static=False):
        return [hash_fn(os.urandom(16)) for _ in range(size)]


def heading(*args):
    print(f'\n{"-" * 50}\n{args[0]}\n{"-" * 50}\n')

def measure(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            print(f"{end_/1000 if end_ > 0 else 0} s")
    return _time_it

def test(name, tree, keys, size):
    root = tree.smtree()
    print(f"{name}")
    print(f"Time for inserting {size} keys:")
    @measure
    def fn():
        r = root
        for key in keys:
            r = tree.update(r, key, key)
        return r

    root = fn()
    print(f"writes: {tree.db.writes}, reads: {tree.db.reads}")
    print(f"root: {root.hex()}")
    print()
    return root


def smt_vs_optsmt(nbyte, size):
    heading("SMT vs. Optimized-SMT")
    hash_fn = blake2b(nbyte)
    keys = gen_keys(size, hash_fn)
    keys_in_order = sorted(keys)
    smtroot=test(
        name="SMT",
        tree=SMT(nbyte, db=Database()),
        keys=keys,
        size=size,
    )
    test(
        name="SMT (Sorted Keys)",
        tree=SMT(nbyte, db=Database()),
        keys=keys_in_order,
        size=size,
    )
    csmrtroot=test(
        name="Optimized-SMT",
        tree=optSMT(nbyte, db=Database()),
        keys=keys,
        size=size,
    )
    test(
        name="Optimized-SMT (Sorted Keys)",
        tree=optSMT(nbyte, db=Database()),
        keys=keys_in_order,
        size=size,
    )
    
    if smtroot==csmrtroot:
        print("Roots of SMT and Optimized SMT are equal")
    else:
        print("Roots of SMT and Optimized SMT are not equal")
    print()


if __name__ == "__main__":
    smt_vs_optsmt(nbyte=32, size=8000)

