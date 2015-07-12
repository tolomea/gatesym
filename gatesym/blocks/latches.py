from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Not, block, nand, Placeholder


@block
def gated_d_latch(data, clock):
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
    l = gated_d_latch(data, clock)
    return gated_d_latch(l, Not(clock))


@block
def register(data, clock):
    res = []
    for i in data:
        res.append(ms_d_flop(i, clock))
    return res
