from gatesym.gates import Not, block, nand, Placeholder


@block
def gated_d_latch(data, clock):
    """ a basic latch that passes and latches the data while the clock is high """
    s = nand(data, clock)
    r = nand(s, clock)
    q = Placeholder(data.network)
    not_q = nand(q, r)
    q.replace(nand(not_q, s))

    # force it to init as 0, this hack is writing the and part of the q nand
    q.network.write(q.actual.node.index, True)
    return q


@block
def ms_d_flop(data, clock):
    """ a two stage latch that clocks data in on a positive edge and out on a negative edge """
    latch = gated_d_latch(data, clock)
    return gated_d_latch(latch, Not(clock))


@block
def register(data, clock):
    """ a bank of ms_d_flops that share a clock line """
    res = []
    for i in data:
        res.append(ms_d_flop(i, clock))
    return res
