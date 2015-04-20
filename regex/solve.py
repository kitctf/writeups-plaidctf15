import re
import itertools
import pycosat
import sys
from collections import defaultdict, Counter

alph = "plaidctf"
size = 171
choices = open('regex.txt').read()[2:-2].split('|')[3:]

clauses = []
def var_x(pos, char):
    return 1 + pos*len(alph) + char

def parse_var(x):
    pos = (x - 1)/len(alph)
    char = (x - 1)%len(alph)
    return (pos, char)

last_var_x = var_x(size, 0)
top = last_var_x
vars_y = {}
def var_y(xs):
    xs = tuple(xs)
    if xs in vars_y:
        return vars_y[xs]
    global top
    var = top
    top += 1
    for x in xs:
        clauses.append((-var, x))
    vars_y[xs] = var
    return var

clauses = []
for pos in range(size):
    clauses.append(tuple(var_x(pos, i) for i in range(len(alph))))

cnt = 0
for r in choices:
    parts = re.findall(r'((?:[^\[])*)\[([^\]]*)\]', r)
    idx = 0
    clause = []
    for space, chars in parts:
        space = sum(int(y or '1') for y in re.findall(r'\.(?:\{(\d+)\})?', space))
        idx += space
        clause.append(var_y(-var_x(idx, alph.index(c)) for c in chars))
        idx += 1
    clauses.append(clause)

N = max(max(map(max,clauses)), -min(map(min,clauses)))
head = "p cnf %d %d" % (N, len(clauses))
print head
with open("instance2.txt", "wb") as f:
    f.write(head + "\n")
    f.write("".join(" ".join(map(str,c)) + " 0\n" for c in clauses))

res = [None]*171
with open("solution2.txt") as f:
    sol = map(int,list(f)[1].split())
    for x in sol:
        if abs(x) < last_var_x and x > 0:
            pos, char = parse_var(x)
            res[pos] = alph[char]
print "".join(res)
