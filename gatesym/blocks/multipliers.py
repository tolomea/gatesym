from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import And, Or, block
from gatesym.blocks.adders import ripple_sum
from gatesym.utils import shuffle_right


@block
def ripple_multiplier(a, b):
    shuffled = []
    for i in range(len(a)):
        shuffled.append(shuffle_right(b, i))
    shuffled_words, shuffled_carries = zip(*shuffled)

    gated_carries = []
    for line, carry in zip(a, shuffled_carries):
        gated_carries.append(And(line, carry))

    gated_words = []
    for line, word in zip(a, shuffled_words):
        gated_words.append([And(line, b) for b in word])

    total, carry = ripple_sum(*gated_words)
    carry = Or(carry, *gated_carries)

    return total, carry
