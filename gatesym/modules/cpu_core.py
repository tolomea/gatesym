from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Not
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_incr
from gatesym.blocks.mux import address_decode, word_switch, word_mux
from gatesym.utils import PlaceholderWord


@block
def cpu_core(clock, data_in):
    network = clock.network
    word_size = len(data_in)

    state = PlaceholderWord(network, 2)
    incr, c = ripple_incr(state)
    state = state.replace(register(incr, clock))

    control_lines = address_decode(state)

    pc = PlaceholderWord(network, word_size)
    incr, c = ripple_incr(pc)
    pc = pc.replace(register(incr, And(clock, state[0])))

    addr = register(data_in, And(clock, Not(state[0])))
    data_out = register(data_in, And(clock, control_lines[1]))

    addr_out = word_mux(state[:1], pc, addr)

    write_out = control_lines[3]

    return addr_out, data_out, write_out
