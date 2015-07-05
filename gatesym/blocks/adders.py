from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import And, Or, Not, block, Tie


@block
def half_adder(a, b):
    carry = And(a, b)
    result = Or(And(a, Not(b)), And(Not(a), b))
    return result, carry


@block
def full_adder(a, b, c):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, c)
    return s2, Or(c1, c2)


@block
def ripple_adder(aw, bw):
    assert len(aw) == len(bw)
    r, c = half_adder(aw[0], bw[0])
    rw = [r]
    for a, b in zip(aw, bw)[1:]:
        r, c = full_adder(a, b, c)
        rw.append(r)
    return rw, c


@block
def ripple_incr(word):
    c = Tie(word[0].network, True)
    rw = []
    for a in word:
        r, c = half_adder(a, c)
        rw.append(r)
    return rw, c


@block
def ripple_sum(*words):
    res, carry = ripple_adder(words[0], words[1])
    for word in words[2:]:
        res, c = ripple_adder(res, word)
        carry = Or(carry, c)
    return res, carry
