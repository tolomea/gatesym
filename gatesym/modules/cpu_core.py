from gatesym.gates import block, And, Or, Placeholder
from gatesym.blocks.latches import register
from gatesym.blocks.adders import ripple_incr
from gatesym.blocks.mux import address_decode, word_switch, word_mux
from gatesym.utils import PlaceholderWord, tie_word


@block
def cpu_core(clock, bus_in, pc_in, write_pc, debug=False):
    """
    the core CPU state machine
    executes a 4 state loop continuously
    s0: fetch address from pc
    s1: maybe fetch address from address
    s2: fetch value from address and increment pc
    s3: fetch address from pc
    s4: maybe fetch address from address
    s5: store value to address and increment pc
    """

    network = clock.network
    word_size = len(bus_in)

    # step through the 6 states in order then reset back to state 0
    state = PlaceholderWord(network, 3)
    s0, s1, s2, s3, s4, s5, s6, s7 = address_decode(state)
    next_state = word_switch(
        [Or(s0, s1, s2, s3, s4), Or(s5, s6, s7)],
        ripple_incr(state)[0],
        tie_word(network, 3),
    )
    state.replace(register(next_state, clock))

    # pc increments in s2 and s5, incoming pc writes from the jump module are taken in s5
    pc = PlaceholderWord(network, word_size)
    incr, c = ripple_incr(pc)
    jumping = And(write_pc, s5)
    new_pc = word_mux([jumping], incr, pc_in)
    clock_pc = And(clock, Or(s2, s5))
    pc.replace(register(new_pc, clock_pc))

    # clock in address in s0 and s3 and s1 and s4 when indirecting
    indirect = Placeholder(network)
    addr = register(bus_in, And(clock, Or(s0, s3, And(indirect, Or(s1, s4)))))
    indirect.replace(addr[-1])

    # set address lines to pc in s0 and s3 and to the previously fetched address in s1, s2, s4 and s5
    addr_out = word_switch([Or(s0, s3), Or(s1, s2, s4, s5)], pc, addr)

    # read in data from bus in s2,
    data = register(bus_in, And(clock, s2))

    # write out data in s5
    write_out = s5
    data_out = data

    if debug:
        clock.watch("clock")
        s0.watch("s0")
        s1.watch("s1")
        s2.watch("s2")
        s3.watch("s3")
        jumping.watch("jumping")
        clock_pc.watch("clock pc")
        write_out.watch("write out")

    return addr_out[:-1], data_out, write_out
