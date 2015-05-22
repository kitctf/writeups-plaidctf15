Clifford
=============

>	"It's a keygen problem"

We are given a binary which asks for an order and a bunch of numbers.
If the numbers are correct, a flag is unobfuscated and printed.

After reversing the code and translating it into a python script, we figured
out which conditions have to be met for the given numbers. The sum of each row
have to be equal and the first number in the first row has to be 9 and the first
number in the second row has to be 11.

You can find the reversed code translated to python in the file "translated_to_python.py"
A hand-drawn image also displays the relationship of the different fields for
orders 2 and 3 (see clifford.jpg).

After knowing the constraints, we got familiar with Z3 and created a bunch of
conditions in Z3 using its python bindings (see solve.py). After executing the
solver, we get a valid solution and the flag if we supply the binary with this
input.
