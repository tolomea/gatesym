from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Or, Not
from gatesym.blocks.latches import register
from gatesym.blocks.mux import word_switch, address_decode


@block
def jump(clock, write, address, data_in):
    """
    allows manipulation of the PC

    address  read  write
    0        PC    PC
    1        PC    dest
    2        PC    if 0: dest -> PC
    3        PC    if !0: dest -> PC
    """

    assert len(address) >= 2
    address = address[:2]

    control_lines = address_decode(address)

    # a destination register for conditional jumps
    write_dest = And(clock, write, control_lines[1])
    dest = register(data_in, write_dest)

    # are we jumping and if so where
    jump_if_zero = And(control_lines[2], Not(Or(*data_in)))
    jump_if_not_zero = And(control_lines[3], Or(*data_in))
    conditional_jump = Or(jump_if_zero, jump_if_not_zero)
    unconditional_jump = control_lines[0]
    write_pc = And(write, Or(conditional_jump, unconditional_jump))
    pc_out = word_switch([conditional_jump, unconditional_jump], dest, data_in)

    return dest, pc_out, write_pc
