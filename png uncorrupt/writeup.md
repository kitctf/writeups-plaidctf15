PNG Uncorrupt
=============

> 	We received this PNG file, but we're a bit concerned the transmission may have not quite been perfect.

Running pngcheck on this file confirms this, the PNG is corrupted.

```
File: corrupt_735acee15fa4f3be8ecd0c6bcf294fd4.png (1188435 bytes)
  File is CORRUPTED.  It seems to have suffered DOS->Unix conversion.
ERRORS DETECTED in corrupt_735acee15fa4f3be8ecd0c6bcf294fd4.png
```

Looking into the file shows a missing `\r` at position 4 of the file, direct in front of a `\n`. So maybe all `\r\n` were converted to `\n` as pngcheck already said.

We wrote a small script to proove this. By parsing the PNG, detecting missing bytes and guessing the missing `\r` infront of `\n`s. Due to the fact, that PNG-blocks conaining an CRC32-Checksum, it is possible to validate each block automaticly.

This lead to the following repairing-script:

```python
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
```



Running this script for about 3 Minutes brings us a readable PNG file, and the flag:

![flag](flag.png)
