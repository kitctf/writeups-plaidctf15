#!/usr/bin/env pypy
import struct
import zlib
import itertools
import re


def fixdata(data, toadd):
	data = data[:-toadd]
	pos = []
	p = 0
	# find possible positions of
	pos = [r.start() for r in re.finditer('\n', data)]
	for todo in itertools.combinations(pos, toadd):
		result = data
		for off, i in enumerate(todo):
			result = result[:i + off] + "\r" + result[i + off:]
		crc = zlib.crc32(result[:-4]) & 0xffffffff
		crc2, = struct.unpack(">I", result[-4:])
		if crc == crc2:
			return result
	return None


out = open("out.png", "w")
f = open("corrupt_735acee15fa4f3be8ecd0c6bcf294fd4.png")
# read and fix PNG-Header
d = f.read(7)
out.write(d[:4] + "\r" + d[4:])
# known PNG block names
ok = ["IHDR", "sBIT", "pHYs", "tEXt", "IDAT", "IEND"]
r = 0
while 1:
	length, = struct.unpack(">I", f.read(4))
	chunk_type = f.read(4)
	if chunk_type not in ok:
		f.seek(-9, 1)
		r += 1
		if r > 10:
			break
		continue
	r = 0
	data = f.read(length + 4)
	b = False
	# Find position offset of next block
	for i in range(5):
		f.read(i)
		if f.read(4) in ok:
			b = True
		f.seek(-i - 4, 1)
		if b:
			break
	# check crc
	crc, = struct.unpack(">I", data[-4:])
	crc2 = zlib.crc32(chunk_type + data[:-4]) & 0xffffffff
	print chunk_type,
	if crc != crc2:
		# find correct block
		fixit = fixdata(chunk_type + data, 4 - i)
		print "block repaird"
		out.write(struct.pack(">I", length))
		assert len(fixit) == length + 8
		out.write(fixit)
		f.seek(-(4 - i), 1)
	else:
		print "block ok"
		out.write(struct.pack(">I", length))
		out.write(chunk_type + data)
		if chunk_type == "IEND":
			exit()
	out.flush()
