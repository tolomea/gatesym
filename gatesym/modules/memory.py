from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Tie
from gatesym.blocks.latches import register
from gatesym.blocks.mux import address_decode, word_switch
from gatesym.utils import tie_word


@block
def memory(clock, write, address, data_in, size):
    """
    a block of RAM

    address  read  write
    N        [N]   [N]
    """
    # address_decode can't deal with empty addresses (aka 1 word memories)
    if not size:
        control_lines = [Tie(clock.network, True)]
    else:
        control_lines = address_decode(address[:size])

    # otherwise it's a simple pile of registers switched by the control lines
    registers = []
    for line in control_lines:
        registers.append(register(data_in, And(line, clock, write)))
    return word_switch(control_lines, *registers)


@block
def rom(clock, write, address, data_in, size, data):
    """
    a block of ROM containing the specified data

    address  read     write
    N        data[N]  -
    """
    network = clock.network
    data_size = len(data_in)
    assert len(data) <= 2**len(address)

    # just ties muxed by address
    control_lines = address_decode(address[:size], len(data))
    ties = [tie_word(network, data_size, d) for d in data]
    return word_switch(control_lines, *ties)
