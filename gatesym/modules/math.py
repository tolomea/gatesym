from gatesym.gates import block, And
from gatesym.utils import pad
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_adder, ripple_subtractor
from gatesym.blocks.multipliers import ripple_multiplier
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


@block
def compact_add(clock, write, address, data_in):
    """
    addition module

    address  read   write
    0        A+B    A
    1        carry  B
    """

    assert len(address) >= 1
    address = address[:1]

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

    return word_switch(control_lines, res, carry)


@block
def combined(clock, write, address, data_in):
    """
    addition module

    address  read    write
    0        A       A
    1        B       B
    2        A+B     -
    3        carry   -
    4        A-B     -
    5        borrow  -
    """

    assert len(address) >= 3
    address = address[:3]

    control_lines = address_decode(address)

    # A register
    write_a = And(clock, write, control_lines[0])
    a = register(data_in, write_a)

    # B register
    write_b = And(clock, write, control_lines[1])
    b = register(data_in, write_b)

    # adder result and carry
    add_res, carry = ripple_adder(a, b)
    carry = pad([carry], len(data_in))

    # subtractor result and borrow
    sub_res, borrow = ripple_subtractor(a, b)
    borrow = pad([borrow], len(data_in))

    return word_switch(control_lines, a, b, add_res, carry, sub_res, borrow)


@block
def mult(clock, write, address, data_in):
    """
    multiplication module

    address  read      write
    0        A         A
    1        B         B
    2        A*B       -
    3        overflow  -
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

    # multiplier result and overflow
    res, overflow = ripple_multiplier(a, b)
    overflow = pad([overflow], len(data_in))

    return word_switch(control_lines, a, b, res, overflow)
