from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Tie
from gatesym.blocks.latches import register
from gatesym.blocks.mux import address_decode, word_switch
from gatesym.utils import tie_word


@block
def memory(clock, write, address, data_in, size):
    address = address[:size]

    write_clock = And(clock, write)

    if size:
        control_lines = address_decode(address)
    else:
        control_lines = [Tie(clock.network, True)]

    registers = []
    for line in control_lines:
        registers.append(register(data_in, And(line, write_clock)))

    return word_switch(control_lines, *registers)


@block
def rom(clock, write, address, data_in, size, data):
    address = address[:size]
    control_lines = address_decode(address, len(data))
    assert len(data) <= len(control_lines)
    network = clock.network
    data_size = len(data_in)
    ties = [tie_word(network, data_size, d) for d in data]
    return word_switch(control_lines, *ties)
