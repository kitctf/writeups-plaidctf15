from Crypto.PublicKey import RSA
import Crypto.Util.number
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import PKCS1_OAEP
import random
from fractions import gcd
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

def crt(a, n):
    lena = len(a)
    p = i = prod = 1; sm = 0
    for i in range(lena): prod *= n[i]
    for i in range(lena):
        p = prod / n[i]
        sm += a[i] * modinv(p, n[i]) * p
    return sm % prod

def dlog_brute_force(x, y, p, M):
    #print x, y, p, M
    return next(e for e in range(p) if pow(x, e, M) == y % M)

def dlog(x, y, ps, M):
    n = 1
    for p in ps:
        n *= p
    cs = []
    for p in ps:
        ni = n / p
        c = dlog_brute_force(pow(x, ni, M), pow(y, ni, M), p, M)
        cs.append(c)
    e = crt(cs, ps)
    assert all(e % p == c for p, c in zip(ps, cs))
    assert pow(x, e, M) == y % M
    return e

def is_prime(p):
    return all(p % d for d in range(2, p))

lo = 269
hi = 787
ps = [2,29]
N = 2*29
for i in range(lo, hi+1):
    if is_prime(i):
        N *= i
        ps += [i]
N += 1
print N
g = 11
#for i in range(100):
    #x = random.randint(i, N)
    #dlog(g, x, ps, N)

def make_key(N, e, d, p, q):
    return RSA.construct((long(N), long(e), long(d), long(p), long(q)))

def pad(c):
    nullkey = make_key(N, 1, 1, 0, 0)
    cipher = PKCS1_OAEP.new(nullkey)
    return cipher.encrypt(c)

def unpad(c):
    nullkey = make_key(N, 1, 1, 0, 0)
    cipher = PKCS1_OAEP.new('\x00' + nullkey)
    return cipher.decrypt(c)

C = Crypto.Util.number.long_to_bytes(g)
def find_key_for_plaintext(pt):
    for i in range(10):
        padded = pad(pt)
        print "Padded: ", repr(padded)
        y = Crypto.Util.number.bytes_to_long(padded)
        #assert padded == Crypto.Util.number.long_to_bytes(y)
        assert y < N
        d = dlog(g, y, ps, N)
        if gcd(d, N-1) == 1:
            e = modinv(d, N-1)%(N-1)
            assert e * d % (N-1) == 1
            return N, d, e
    assert 0

m0 = "I hereby commit to a guess of 0"
m1 = "I hereby commit to a guess of 1"
N0, d0, e0 = find_key_for_plaintext(m0)
print "N0=",N0
print "d0=",d0
print "e0=",e0
N1, d1, e1 = find_key_for_plaintext(m1)
print "N1=",N1
print "d1=",d1
print "e1=",e1
key0 = make_key(N0, e0, d0, 0, 0)
key1 = make_key(N1, e1, d1, 0, 0)
#print 'key0 = """%s"""' % key0.exportKey()
#print 'key1 = """%s"""' % key0.exportKey()
sz = (Crypto.Util.number.size(N) + 7) // 8
C = C.rjust(sz, '\x00')
print 'C = %s' % repr(C)

def decrypt(N, d, e, C):
    key = make_key(N, e, d, 0, 0)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(C)

print decrypt(N0, d0, e0, C)
print decrypt(N1, d1, e1, C)
