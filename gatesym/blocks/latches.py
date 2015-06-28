from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import And, Not, block, nand


@block
def gated_d_latch(data, clock):
    s = nand(data, clock)
    r = nand(s, clock)
    q1 = And(s)
    q2 = Not(q1)
    nq = nand(q2, r)
    q1.add_input(nq)
    return q2


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
