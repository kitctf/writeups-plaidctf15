#!/usr/bin/env python

# https://raw.githubusercontent.com/comawill/sock/master/sock.py
from sock import Sock
from Crypto.PublicKey import RSA, DSA

from Crypto.Cipher import PKCS1_OAEP
import re

def chunks(l, n):
	""" Yield successive n-sized chunks from l.
	"""
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

if __name__ == "__main__":
	_pub_enc =  RSA.importKey('-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDGRrsdIqf8K39Ncwzsi9k2lr5G\nJ8aEFkYGrYqOQRbU5xOReMj8wWHgnSUC0fjH0gjffGiUC2HfrrNIQvXKGiSBetOu\nIWOmFiESG8IhrPyvLwX53NbMWeCihzbYGJxGyiL0bvDHxqDxzuvteSaEfNm1miPA\nQ9rs5vFnHM0R3kFjdQIDAQAB\n-----END PUBLIC KEY-----')

	pub_enc = PKCS1_OAEP.new(_pub_enc)
	
	pub_sig =  DSA.construct([6492988819243051335053735606322819439099395961135352303030066825351059776939776358522765113843576255727411249922052441719518573282010295240606387519552263L,5720927070571587652595864015095152811124313453716975619963331476834195150780326792550956895343289380256771573459290257563350163686508250507929578552744739L,6703916277208300332610863417051397338268350992976752494932363399494412092698152568009978917952727431041521105933065433917303157931689721949082879497208537,1022875313346435070370368907571603203095488145799L])




	key = DSA.generate(512)
	rsa_key = RSA.generate(1024)
	rsa = PKCS1_OAEP.new(rsa_key)

	C = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0b'
	keys = [
	"""-----BEGIN RSA PRIVATE KEY-----
	MIIBLwIBAAJdFbWLEZXQ/YNUggW8nuMZL9GsimufYcyze6ODuPYKQFaD6UF5+ZdF1tIDzIybjNxF
	2fNeTgQ+LrXT+4BVNWrA0bjewtGDRxCoJ5S1h6TwCzc0NfeOSbNhZyHGEt7XAl0FrFoCiyOIYYyL
	qBlGm4tvesewywhcnGe1trtl3cS63Y0ztvVVeAkdlUzBcSs2lzVAV6756ZViBZpSHZgCJHAje2sv
	rI0hTKROZNm16R3nMJGuTjWfPg3nvu/JcLsCXQewj1RVdeHi31Pf+0gbnSkeTn1+Sktgr2pHPpYG
	aKHA7XrhroTJ4LmxaJ2511D9GaGB7tM5GGirKs6guBTZ0aMvsqn34SaCJntMpimZJMJD8PuClV/2
	vhtdlwcBgwIBAAIBAAIBAAIBAAIBAA==
	-----END RSA PRIVATE KEY-----""",
	"""-----BEGIN RSA PRIVATE KEY-----
	MIIBLwIBAAJdFbWLEZXQ/YNUggW8nuMZL9GsimufYcyze6ODuPYKQFaD6UF5+ZdF1tIDzIybjNxF
	2fNeTgQ+LrXT+4BVNWrA0bjewtGDRxCoJ5S1h6TwCzc0NfeOSbNhZyHGEt7XAl0GZ5MrsV44uF2q
	d15/Na/y8z5gf5Hfz+tSiJ0L+o7NOZ5D2tx+1eLJlM0oGLKduwpeffTCZl6oSBTfOxANB0Zuh87Q
	OLGX7+ScVGe3AJ4mj488BAHg/a7MOeuVJNUCXRMWs1CSrylXM+IbaRGIvFuyQvHAuhx9usMscgeH
	aaGBVTUp4RoGxMFwqOX+1g9EVV8Nua+AnAk5WfqUzxKmEo6t6lKb+csD4voaeKZZE7IeEKLHhdl0
	Bir/nMW/lQIBAAIBAAIBAAIBAAIBAA==
	-----END RSA PRIVATE KEY-----"""
	]



	#print pub_enc.encrypt(4,None)
	pk = [str(key.__getstate__()[x]) for x in key.keydata[:-1]]
	pk_str = ",".join(pk)
	#crypto = pub_enc.encrypt(pk_str, None)
	#maxlen = (len(str(hex((_pub_enc.__getstate__())["n"])))-3)/2
	#print maxlen
	bla = ",".join([pub_enc.encrypt(c).encode("hex") for c in chunks(pk_str, 64)])
	s = Sock("52.6.11.111", 4321)
	s.read_until("communications\n")
	s.send(bla)
	returnv = s.read_until("\n").split(" (")[1].split("), ")[0]
	
	f = dict(key.__getstate__())
	del f["x"]
	#print f
	assert str(f) == returnv
	print s.read_until("\n")
	print s.read_until("\n")
	print "..."
	while 1:
		line = s.read_until("\n").strip()
		print line
		if "shit" in line:
			exit()
		have = int(re.search(r'\$(\d+)', line).group(1))
		print have
		#print line
		bet = have
		ods = 2
		guess = 1
		print "> lets bet %d" % bet
		s.send("%d\n" % bet)
		print s.read_until("\n").strip()
		print "> odds are at %d" % ods
		s.send("%d\n" % ods)
		print s.read_until("\n").strip()
		guess_str = "I hereby commit to a guess of %d" % guess
		guess_str = rsa.encrypt
		guess_str = C
		guess_str_enc = guess_str.encode('hex')
		#guess_str_enc = ",".join([rsa.encrypt(c).encode("hex") for c in chunks(guess_str, 64)])

		sig = ",".join(map(str,key.sign(guess_str_enc, 2L)))
		print "> send guess"
		s.send("%s~%s" % (guess_str_enc, sig))

		s.read_until("\n").strip() # generating random
		s.read_until("\n").strip() #beep
		rng = long(s.read_until("\n").strip().split(" ")[-1])
		print rng
		print s.read_until("\n").strip()
		#OLD rsa_priv = rsa_key.exportKey()
		rsa_priv = keys[rng%2]
		sig_priv = ",".join(map(str,key.sign(rsa_priv, 2L)))
		print "> send key"
		s.send("%s~%s" % (rsa_priv, sig_priv))
		print s.read_until("\n")
	print "]]"
	s.telnet()
	#print bla
	#print len(pk_str)
	#print len(crypto[0])
