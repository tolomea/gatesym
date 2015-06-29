from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And
from gatesym.blocks.latches import register
from gatesym.blocks.mux import address_decode, word_switch


@block
def memory(clock, write, address, data_in):
    write_clock = And(clock, write)

    control_lines = address_decode(address)

    registers = []
    for line in control_lines:
        registers.append(register(data_in, And(line, write_clock)))

    return word_switch(control_lines, *registers)
