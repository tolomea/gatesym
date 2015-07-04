from __future__ import unicode_literals, division, absolute_import


from gatesym.gates import Tie


def pad(word, length, value=False):
    tie = Tie(word[0].network, value)
    return word + [tie] * (length - len(word))


def tie_register(network, size, value=0):
    res = []
    for i in range(size):
        res.append(Tie(network, value=value % 2))
        value //= 2
    return res
