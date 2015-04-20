import struct
import sys
from base64 import *
from fractions import *

def eval_frac(c):
    x = Fraction(c[-1])
    for y in reversed(c[:-1]):
        x = 1/x + y
    return x

def cont_frac(x):
    while True:
        i = x // 1
        yield i
        if x == i: break
        x = 1 / (x - i)

def convergents(x):
    c = list(cont_frac(x))
    for i in xrange(1, len(c)):
        yield eval_frac(c[:i])
    yield x

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

def isqrt(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi)/2
        if mid*mid >= x: hi = mid
        else: lo = mid + 1
    return lo if lo*lo == x else None

def wiener(e, n):
    for x in convergents(Fraction(e,n)):
        k = x.numerator
        d = x.denominator
        if not k: continue
        phi = Fraction(e*d - 1, k)
        a = 1
        b = -(n-phi+1)
        c = n
        disc = b*b-4*a*c
        if b*b-4*a*c > 0:
            if long(disc) != disc: continue
            s = isqrt(long(disc))
            if not s: continue
            if (-b + s) % (2*a): continue
            p = (-b + s) // (2*a)
            q = (-b - s) // (2*a)
            assert (p-1)*(q-1) == phi
            if p * q == n:
                d = modinv(e, phi)
                return p, q, d
    return None

if __name__ == "__main__":
    # read pubkey in SSH format
    dat = b64decode(sys.stdin.read().split()[1])
    fields = []
    while dat:
        sz = struct.unpack('>I', dat[:4])[0]
        fields.append(dat[4:4+sz])
        dat = dat[4+sz:]

    e = eval('0x' + fields[1].encode('hex'))
    n = eval('0x' + fields[2].encode('hex'))

    p, q, d = wiener(e, n)
    print "n =", n
    print "p =", p
    print "q =", q
    print "e =", e
    print "d =", d
