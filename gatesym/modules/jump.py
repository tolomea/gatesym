from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Or, Not
from gatesym.blocks.latches import register
from gatesym.blocks.mux import word_switch, address_decode


@block
def jump(clock, write, address, data_in):
    assert len(address) >= 2
    address = address[:2]

    control_lines = address_decode(address)

    write_dest = And(clock, write, control_lines[1])
    dest = register(data_in, write_dest)

    jump_zero = And(write, control_lines[2], Not(Or(*data_in)))

    jump = And(write, control_lines[0])

    write_pc = Or(jump, jump_zero)
    pc_out = word_switch([jump, jump_zero], data_in, dest)
    return dest, pc_out, write_pc
