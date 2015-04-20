from fractions import gcd
from ast import literal_eval
import sys

def ex_gcd(a, b):
    x1 = 0; y1 = 1
    x = 1; y = 0
    while b:
        q = a / b; r = a % b
        x2 = x - q * x1; y2 = y - q * y1
        a = b; b = r; x = x1; x1 = x2; y = y1; y1 = y2
    return a, x, y

def modinv(x, N):
    g, alpha, _ = ex_gcd(x, N)
    assert alpha * x % N == 1
    return alpha

def powmod(x, e, N):
    if e >= 0:
        return pow(x, e, N)
    inv = modinv(x, N)
    return pow(inv, -e, N)

es = []
cs = []
with open('captured_827a1815859149337d928a8a2c88f89f') as f:
    next(f)
    for l in f:
        N, e, c = [literal_eval(x.strip()) for x in l.strip()[1:-1].split(':')]
        es.append(e)
        cs.append(c)

for i in range(len(es)):
    for j in range(i+1,len(es)):
        e1 = es[i]
        e2 = es[j]
        g, s, t = ex_gcd(e1, e2)
        if g == 1:
            c1 = cs[i]
            c2 = cs[j]
            M = (powmod(c1, s, N) * powmod(c2, t, N)) % N
            assert pow(M, e1, N) == c1
            print hex(M)[2:-1].decode('hex')
