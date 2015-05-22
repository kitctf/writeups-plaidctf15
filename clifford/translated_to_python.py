#!/usr/bin/env python

import sys

def main():
	order = int(sys.argv[1])

	if order <= 1 or order > 10:
		print "No good order"
		sys.exit(1)

	num_pointers = 2 * order - 1

	numbers = [0]*num_pointers

	for i in range(num_pointers):
		numbers[i] = [0]*(i+order)

	print numbers

	v11 = 3 * order * order + -3 * order + 1

	for j in range(order):
		for k in range(j+order):
			numbers[j][k] = int(raw_input("Number: "))

	print numbers

	for l in range(order, 2 * order - 1):
		v12 = 2*order - 1 + ~(l-order)
		v13 = l - order + 1

		for m in range(v12):
			numbers[l][m+v13] = int(raw_input("Number2: "))

	print numbers

	print("Verifying...")
	if not verify(numbers, order):
		print("Incorrect")
	else:
		print("Correct")

def verify(numbers, order):
	bufcount = 3 * order * order + -3 * order + 1
	buffer = [0] * (bufcount)

	#zaehlt vorkommen aller zahlen in entsprechendem arrayelement in <buffer>
	for i in range(2*order-1):
		for j in range(order+i):
			v25 = numbers[i][j]
			
			if bufcount < v25:
				print "Condition 1 failed: all numbers must be > than the count of read numbers"
				return False
			
			if v25 < 0:
				print "Condition 2 failed: no numbers < 0"
				return False

			if v25 > 0:
				print "Incrementing ", v25-1
				buffer[v25 - 1]+=1

	v6 = 0
	for k in range(bufcount):
		v6 += buffer[k]
		if buffer[k] > 1:
			print "Condition 3 failed: number %d occured more than once" % k
			return False

	#keine nullen...
	if bufcount == v6:
		sum_firstline = 0
		for l in range(order):
			sum_firstline += numbers[0][l]

		print "sum_firstline", sum_firstline

		for m in range(2*order - 1):
			v11 = 0
			for n in range(order + m):
				print m, n
				v11 += numbers[m][n]

			print ""
			if v11 != sum_firstline:
				print "Condition 5 failed in m=%d" % m
				return False

		print ""
		print ""

		for ii in range(order):
			v14 = 0
			for jj in range(order + ii):
				print jj, ii
				v14 += numbers[jj][ii]

			print ""
			if v14 != sum_firstline:
				print "Condition 6 failed in ii=%d" % ii
				return False

		print ""
		print ""

		for kk in range(order, 2*order-1):
			v17 = 0
			for ll in range(2*order - 1 + ~(kk-order)):
				print ll + kk - order + 1, kk
				v17 += numbers[ll + kk - order + 1][kk]

			print ""
			if v17 != sum_firstline:
				print "Condition 7 failed in kk=%d" % kk
				return False

		print ""
		print ""

		for mm in range(order):
			v20 = 0
			for nn in range(2*order-1-mm):
				print mm+nn, nn
				v20 += numbers[mm+nn][nn]

			print ""
			if v20 != sum_firstline:
				print "Condition 8 failed in mm=%d" % mm
				return False

		print ""
		print ""

		for i1 in range(1, order):
			v23 = 0
			for i2 in range(2 * order - 1 - i1):
				print i2, i1 + i2
				v23 += numbers[i2][i1 + i2]

			print ""
			if v20 != sum_firstline:
				print "Condition 9 failed in i2=%d" % i2
				return False

		if numbers[0][0] + numbers[1][0] == 20:
			if numbers[0][0] == 9:
				return True
			else:
				print "Condition 10 failed"
				return False
		else:
			print "Condition 11 failed"

	else:
		print "Condition 4 failed: ..."
		return False


if __name__ == '__main__':
	main()
