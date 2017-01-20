from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And
from gatesym.utils import pad
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_adder, ripple_subtractor
from gatesym.blocks.mux import word_switch, address_decode


@block
def add(clock, write, address, data_in):
    """
    addition module

    address  read   write
    0        A      A
    1        B      B
    2        A+B    -
    3        carry  -
    """

    assert len(address) >= 2
    address = address[:2]

    control_lines = address_decode(address)

    # A register
    write_a = And(clock, write, control_lines[0])
    a = register(data_in, write_a)

    # B register
    write_b = And(clock, write, control_lines[1])
    b = register(data_in, write_b)

    # adder result and carry
    res, carry = ripple_adder(a, b)
    carry = pad([carry], len(data_in))

    return word_switch(control_lines, a, b, res, carry)


@block
def sub(clock, write, address, data_in):
    """
    subtraction module

    address  read    write
    0        A       A
    1        B       B
    2        A-B     -
    3        borrow  -
    """
    assert len(address) >= 2
    address = address[:2]

    control_lines = address_decode(address)

    # A register
    write_a = And(clock, write, control_lines[0])
    a = register(data_in, write_a)

    # B register
    write_b = And(clock, write, control_lines[1])
    b = register(data_in, write_b)

    # subtractor result and borrow
    res, borrow = ripple_subtractor(a, b)
    borrow = pad([borrow], len(data_in))

    return word_switch(control_lines, a, b, res, borrow)
