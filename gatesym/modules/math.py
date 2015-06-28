from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Not, Tie
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_adder
from gatesym.blocks.mux import word_mux


@block
def add(clock, write, address, data_in):
    assert len(address) == 2

    write_a = And(clock, write, Not(address[0]), Not(address[1]))
    a = register(data_in, write_a)

    write_b = And(clock, write, address[0], Not(address[1]))
    b = register(data_in, write_b)

    res, carry = ripple_adder(a, b)
    carry = [carry] + [Tie(address[0].network) for i in range(len(data_in)-1)]

    return word_mux(address, a, b, res, carry)
