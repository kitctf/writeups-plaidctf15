#!/usr/bin/env python

from z3 import *

s = Solver()

order = 3

max_valid_input = 3 * order * order + -3 * order + 1
min_valid_input = 0

rows = 2*order-1
colums = order

#used fields in grid
used_fields = []
for j in range(order):
	for k in range(j+order):
		used_fields += [(j,k)]

for l in range(order, 2 * order - 1):
	v12 = 2*order - 1 + ~(l-order)
	v13 = l - order + 1
	for m in range(v12):
		used_fields += [(l,m+v13)]

#all fields in grid
all_fields = []
for y in range(rows):
	for x in range(colums+y):
		all_fields += [(y,x)]

#unused fields in grid (always 0)
unused_fields = list(set(all_fields) - set(used_fields))

#grid for z3
grid = [[Int("X{0}_{1}".format(y, x)) for x in range(colums+y)] for y in range(rows)]
print grid

#add constraints for used fields
for y,x in used_fields:
	s.add(And(grid[y][x] > min_valid_input, grid[y][x] <= max_valid_input))

#add constraints for unused fields (always 0)
for y,x in unused_fields:
	s.add(grid[y][x] == 0)

#all used fields have to be distinct
s.add(Distinct([grid[y][x] for (y,x) in used_fields]))

#add known fields
s.add(grid[0][0] == 9)
s.add(grid[1][0] == 11)
s.add(grid[0][0] + grid[1][0] == 20)

#sum of the first line, all following conditions are sums which have to equal this sum and thereby equal to each other
firstline_sum = Sum(grid[0])

#Condition 5
#sum of all horizontal
horizontal_rows = [[grid[m][n] for n in range(order + m)] for m in range(2*order - 1)]
horizontal_row_sums = [Sum(r) for r in horizontal_rows]
for sum in horizontal_row_sums:
	s.add(sum == firstline_sum)

#Condition 6
vals = [[grid[jj][ii] for jj in range(order + ii)] for ii in range(order)]
vals_sum = [Sum(r) for r in vals]
for sum in vals_sum:
	s.add(sum == firstline_sum)

#Condition 7
vals = [[grid[ll + kk - order + 1][kk] for ll in range(2*order - 1 + ~(kk-order))] for kk in range(order, 2*order-1)]
vals_sum = [Sum(r) for r in vals]
for sum in vals_sum:
	s.add(sum == firstline_sum)

#Condition 8
vals = [[grid[mm+nn][nn] for nn in range(2*order-1-mm)] for mm in range(order)]
vals_sum = [Sum(r) for r in vals]
for sum in vals_sum:
	s.add(sum == firstline_sum)

#Condition 9
vals = [[grid[i2][i1 + i2] for i2 in range(2 * order - 1 - i1)] for i1 in range(1, order)]
vals_sum = [Sum(r) for r in vals]
for sum in vals_sum:
	s.add(sum == firstline_sum)

print s

if s.check() == sat:
	m = s.model()
	for (y,x) in used_fields:
		print (y,x), m.eval(grid[y][x])

	string = ""
	for (y,x) in used_fields:
		string += str(m.eval(grid[y][x])) + " "
	print string

else:
	print "No solution"
