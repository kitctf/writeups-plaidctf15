from fractions import gcd
from ast import literal_eval
import sys
import wiener

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

with open('captured_a4ff19205b4a6b0a221111296439b9c7') as f:
    next(f)
    for l in f:
        N, e, c = [literal_eval(x.strip()) for x in l.strip()[1:-1].split(':')]
        print "Checking..."
        res = wiener.wiener(e, N)
        if res:
            print "YES"
            P, Q, D = res
            m = powmod(c, D, N)
            print hex(m)[2:-1].decode("hex")
