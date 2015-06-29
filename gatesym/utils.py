from __future__ import unicode_literals, division, absolute_import


from gatesym.gates import Tie


def pad(word, length, value=False):
    tie = Tie(word[0].network, value)
    return word + [tie] * (length - len(word))
