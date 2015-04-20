import socket
import struct
import sys

TARGET=('52.4.141.125', 4141)
if len(sys.argv) > 1 and sys.argv[1] == 'l':
    TARGET=('127.0.0.1', 4141)

def get_master_key():
    res = ''
    for i in range(2):
        s = socket.create_connection(TARGET)
        code = [
            struct.pack('BBBBI', 0, 0, 2*i + 4, 0, 0),
            struct.pack('BBBBI', 0, 1, 2*i + 5, 0, 0),
            struct.pack('BBBBI', 0xc, 0, 0, 0, 0),
        ]
        plaintext = 'A'*8
        iv = 'B'*8
        s.send(struct.pack('II', len(code), len(plaintext)))
        s.send(iv)
        s.send(''.join(code))
        s.send(plaintext)
        res += s.recv(4096)
    return res

def decode(ins, offset):
    code = ord(ins[0])
    o1 = 'r[%d]' % ord(ins[1])
    o2 = 'r[%d]' % ord(ins[2])
    o3 = 'r[%d]' % ord(ins[3])
    const = struct.unpack('I', ins[4:])[0]
    name = {2: '+', 3: '&', 4: '|', 5: '^', 7: '>>', 8: '<<'}.get(code)
    if code == 0:
        return '%s = %s' % (o1, o2)
    if code == 1:
        return '%s = 0x%x' % (o1, const)
    if 2 <= code <= 5:
        return '%s = (%s %s %s) & 0xffffffff' % (o1, o2, name, o3)
    if 7 <= code <= 8:
        return '%s = (%s %s %d) & 0xffffffff' % (o1, o2, name, const)
    if 9 == code:
        return '%s = r[%d + %s]' % (o1, ord(ins[2]), o3)
    if 0xb == code:
        return 'jl %s, %s, ->%04x' % (o2, o3, const)
    if 0xc == code:
        return 'exit'
    return prefix

def local(iv, plaintext):
    iv0, iv1 = struct.unpack("II", iv)
    p0, p1 = struct.unpack("II", plaintext)
    key = struct.unpack("IIII", master_key)
    r = [None]*16
    r[0] = iv0
    r[1] = iv1
    r[2] = p0
    r[3] = p1
    r[4:8] = key
    r[0] = (r[0] ^ r[2]) & 0xffffffff
    r[1] = (r[1] ^ r[3]) & 0xffffffff
    r[15] = 0x0
    r[14] = 0x9e3779b9
    r[13] = 0x0
    while 1:
        r[2] = (r[1] << 4) & 0xffffffff
        r[3] = (r[1] >> 5) & 0xffffffff
        r[2] = (r[2] ^ r[3]) & 0xffffffff
        r[2] = (r[2] + r[1]) & 0xffffffff
        r[12] = 0x3
        r[11] = (r[13] & r[12]) & 0xffffffff
        r[10] = r[4 + r[11]]
        r[10] = (r[10] + r[13]) & 0xffffffff
        r[2] = (r[2] ^ r[10]) & 0xffffffff
        r[0] = (r[0] + r[2]) & 0xffffffff
        r[13] = (r[13] + r[14]) & 0xffffffff
        r[2] = (r[0] << 4) & 0xffffffff
        r[3] = (r[0] >> 5) & 0xffffffff
        r[2] = (r[2] ^ r[3]) & 0xffffffff
        r[2] = (r[2] + r[0]) & 0xffffffff
        r[12] = 0x3
        r[9] = (r[13] >> 11) & 0xffffffff
        r[11] = (r[9] & r[12]) & 0xffffffff
        r[10] = r[4 + r[11]]
        r[10] = (r[10] + r[13]) & 0xffffffff
        r[2] = (r[2] ^ r[10]) & 0xffffffff
        r[1] = (r[1] + r[2]) & 0xffffffff
        r[8] = 0x1
        r[15] = (r[15] + r[8]) & 0xffffffff
        r[8] = 0x40
        if r[15] >= r[8]:
            break
    return struct.pack("II", r[0], r[1])

def local2(iv, plaintext):
    iv0, iv1 = struct.unpack("II", iv)
    a, b = struct.unpack("II", plaintext)
    key = struct.unpack("IIII", master_key)
    r = [None]*16
    iv0 ^= a
    iv1 ^= b
    acc = 0
    for _ in range(rounds):
        a = (((iv1 << 4) ^ (iv1 >> 5)) + iv1) &0xffffffff
        a ^= (key[acc % 4] + acc) & 0xffffffff
        iv0 = (iv0 + a) & 0xffffffff
        acc = (acc + 0x9e3779b9) & 0xffffffff
        a = (((iv0 << 4) ^ (iv0 >> 5)) + iv0) & 0xffffffff
        a ^= (key[(acc >> 11) % 4] + acc) & 0xffffffff
        iv1 = (iv1 + a) & 0xffffffff
    return struct.pack("II", iv0, iv1)

def reverse(iv, ciphertext):
    iv0, iv1 = struct.unpack("II", ciphertext)
    key = struct.unpack("IIII", master_key)
    acc = 0
    for i in range(rounds):
        acc = (acc+0x9e3779b9) & 0xffffffff
    for _ in range(rounds):
        a = (((iv0 << 4) ^ (iv0 >> 5)) + iv0) & 0xffffffff
        a ^= (key[(acc >> 11) % 4] + acc) & 0xffffffff
        iv1 = (iv1 - a) & 0xffffffff
        acc = (acc-0x9e3779b9) & 0xffffffff
        a = (((iv1 << 4) ^ (iv1 >> 5)) + iv1) &0xffffffff
        a ^= (key[acc % 4] + acc) & 0xffffffff
        iv0 = (iv0 - a) & 0xffffffff
    assert acc == 0
    a, b = struct.unpack("II", iv)
    iv0 ^= a
    iv1 ^= b
    return struct.pack("II", iv0, iv1)

def remote(iv, plaintext):
    s = socket.create_connection(TARGET)
    s.send(struct.pack('II', len(code)//8, len(plaintext)))
    s.send(iv)
    s.send(code)
    s.send(plaintext)
    res = s.recv(4096)
    assert len(res) == 8
    return res

stream = open('stream.raw', 'rb').read()
code = stream[2*8:2*8 + 0x20*8]
rounds = 0x40
for i in range(0, len(code), 8):
    ins = code[i:i+8]
    print decode(ins, i / 8)

iv = 'a'*8
plaintext = 'b'*8
master_key = 'c'*16
assert reverse(iv, local2(iv, plaintext)) == plaintext

master_key = get_master_key()
print "[+] Master key =", master_key.encode('hex')
assert local2(iv, plaintext) == remote(iv, plaintext)

res = ""
iv = stream[8:16]
ciphertext = stream[0x1eb:]
for i in range(0, len(ciphertext), 8):
    res += reverse(iv, ciphertext[i:i+8])
    iv = ciphertext[i:i+8]
print res
