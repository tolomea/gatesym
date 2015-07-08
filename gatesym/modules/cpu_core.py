from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And, Or
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_incr
from gatesym.blocks.mux import address_decode, word_switch
from gatesym.utils import PlaceholderWord


@block
def cpu_core(clock, data_in):
    network = clock.network
    word_size = len(data_in)

    # step through the 4 states in order
    state = PlaceholderWord(network, 2)
    incr, c = ripple_incr(state)
    state = state.replace(register(incr, clock))
    s0, s1, s2, s3 = address_decode(state)

    # pc increments in s1 and s3
    pc = PlaceholderWord(network, word_size)
    incr, c = ripple_incr(pc)
    clock_pc = And(clock, Or(s1, s3))
    pc = pc.replace(register(incr, clock_pc))

    # clock in address in s0 and s2
    addr = register(data_in, And(clock, Or(s0, s2)))

    # send address as pc in s0 and s2 and addr in s1 and s3
    addr_out = word_switch([Or(s0, s2), Or(s1, s3)], pc, addr)

    # write out data in stage3
    write_out = s3
    data_out = register(data_in, And(clock, s1))

    return addr_out, data_out, write_out
