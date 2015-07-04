from __future__ import unicode_literals, division, absolute_import

import collections

from gatesym.gates import Tie, Placeholder


def pad(word, length, value=False):
    tie = Tie(word[0].network, value)
    return word + [tie] * (length - len(word))


def tie_word(network, size, value=0):
    res = []
    for i in range(size):
        res.append(Tie(network, value=value % 2))
        value //= 2
    return res


class PlaceholderWord(collections.Sequence):
    def __init__(self, network, size):
        self.placeholders = [Placeholder(network) for i in range(size)]

    def __len__(self):
        return len(self.placeholders)

    def __getitem__(self, index):
        return self.placeholders[index]

    def replace(self, inputs):
        return [old.replace(new) for old, new in zip(self, inputs)]
