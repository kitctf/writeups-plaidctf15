#!/usr/bin/env python2

import struct
import math

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

ror = lambda val, r_bits, max_bits: \
            ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
                (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
def ROR4(x, n):
    return ror(x,n,32)

def mangle_A(buf):
    x = ROR4(buf[1]&buf[2]|buf[3]&~buf[1], 25)
    return [buf[3], (buf[1]+(buf[0]^x))&0xffffffff, buf[1], buf[2]]

def unmangle_A(m):
    buf3, xord, buf1, buf2 = m
    x = ROR4(buf1&buf2|buf3&~buf1, 25)
    buf0 = ((xord - buf1) % 2**32 ) ^ x
    return [buf0, buf1, buf2, buf3]

def mangle_B(buf):
    x = ROR4(buf[3] & buf[1] | buf[2] & ~buf[3], 25)
    return [buf[3], (buf[1]+(buf[0]^x))&0xffffffff, buf[1], buf[2]]

def unmangle_B(m):
    buf3, xord, buf1, buf2 = m
    x = ROR4(buf3 & buf1 | buf2 & ~buf3, 25)
    buf0 = ((xord - buf1) % 2**32 ) ^ x
    return [buf0, buf1, buf2, buf3]

def mangle_C(buf):
    x = ROR4(buf[2]^buf[1]^buf[3], 25)
    return [buf[3], (buf[1]+(buf[0]^x))&0xffffffff, buf[1], buf[2]]

def unmangle_C(m):
    buf3, xord, buf1, buf2 = m
    x = ROR4(buf2^buf1^buf3, 25)
    buf0 = ((xord - buf1) % 2**32 ) ^ x
    return [buf0, buf1, buf2, buf3]

def mangle_D(buf):
    x = ROR4(buf[2]^(buf[1]|~buf[3]), 25)
    ret = [buf[3], (buf[1]+(buf[0]^x))&0xffffffff, buf[1], buf[2]]
    return ret

def unmangle_D(m):
    buf3, xord, buf1, buf2 = m
    x = ROR4(buf2^(buf1|~buf3), 25)
    buf0 = ((xord - buf1) % 2**32 ) ^ x
    return [buf0, buf1, buf2, buf3]

def get_byte(i, j, n, inp):
    pos = i*n+j
    if 2*pos + 1 > len(inp):
        return "00"
    return inp[2*pos:2*pos+2]

def unrotate(buf):
    buf = list(reversed(buf))
    n = int(math.sqrt(len(buf)*4))
    string = ""
    for dw in buf:
        string += "%08x" % dw

    result = ""
    for i in xrange(n):
        for j in range(n):
            result += get_byte(j,i,n,string)
    return list(reversed([struct.unpack('<I', result[i:i+8].decode('hex'))[0] for i in range(0, len(result), 8)]))

def solve(dwords):
    for i in reversed(xrange(0x80)):
        dwords = unrotate(dwords)
        for chunk in range(0, len(dwords), 4):
            chbuf = dwords[chunk:chunk+4]
            if i&0x3f > 31 and i&0x1f > 15:
                chbuf = unmangle_D(chbuf)
            elif i&0x3f > 31 and i&0x1f <= 15:
                chbuf = unmangle_C(chbuf)
            elif i&0x3f <= 31 and i&0x1f > 15:
                chbuf = unmangle_B(chbuf)
            elif i&0x3f <= 31 and i&0x1f <= 15:
                chbuf = unmangle_A(chbuf)
            dwords = dwords[0:chunk] + chbuf + dwords[chunk+4:]
    return dwords

flag = "The flag is *not* poop, but you can try that anyway because you strings'd this binary and saw something that looked interesting and just had to try it..." + '\x00\x00\x00'
buf = map(lambda x: struct.unpack('<I', x)[0], [chunk for chunk in chunks(flag, 4)])
buf = solve(buf)
print ''.join(struct.pack('<I', d).encode('hex') for d in buf)