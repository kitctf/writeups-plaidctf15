ECE's Revenge
=============

>	Okay, well we didn't have time to make a circuit board for you all. But we do have this.

We are given a verilog source code file together with a testbench.
The logic defined is supplied with signals like the clock and reset as well
as a 32 bit wide user input and a win-signal which indicates a correct input
of the user data.

The goal is to figure out the correct user data input.

When looking at the verilog code we see that it consists of four basic blocks
which are instantiated a few times each:

part_a: a D-flip-flop
part_b: a half-adder
part_c: a multiplexer
part_d: a 4 bit counter

Whe following the user_input signal, we see that it is supplied to 4 MUXes.
The muxes select one bit out of eight of each byte of the user input using the
lowermost 3 bits of the signal is_i.

is_i is a concatenation of the outputs of two 4-bit counters. These counters
are wired up in a way that the first counter ticks with every clock cycle and
the second increments only on a falling-edge of the highest bit of the output
of the first counter. Essentially, these two counters form an 8 bit counter.

So the muxes just select the bits 0 to 7 of each user input byte.
These selected bits (0, 8, 16, 24 or 1, 9, 17, 24 and so on...) are then concatenated
and fed into another mux which selects one bit using the bits 5 to 3 of the is_i
counter signal.
The resulting signal is called im_f and just contains the bits 0 to 31 of the input
data in sequence advanced each clock cycle.

Next, we traced the win-output so that we could figure out what we have to do, to
assert it. We followed it to a combinatoric assignment called 'win_in' which gets
asserted either if win already was high before or if the counter reached a specific
value and the signal w_t is not asserted.

Tracing w_t leads us to another combinatoric assignment which ors two signals
i_g_o and out_x1. We see that i_g_o is a signal buffered by a flip flop. The input
of this flip flop is w_t which means, that once w_t switches to high, it stays
this way. This is something we don't want, because it directly influences the win
output bit.

The other side of this assignment, out_x1 is defined by the xor operation of
im_f and m_o. We know that im_f is the selected bit of the user input and we
know that we want to keep the result out_x1 always low. In order to do that, we
need to keep im_f and m_o always the same. im_f is our supplied input, so m_o
needs to be some sequence which has to be euqal to our input.

We then threw the code into Vivado to simulate it, wrote down the sequence of
m_o and moved it around to align it with the selected bits of the user input.
As soon at it matched, we saw the win-output go high and we had the solution.
