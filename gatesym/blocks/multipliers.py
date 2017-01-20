from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import And, Or, block
from gatesym.blocks.adders import ripple_sum
from gatesym.utils import shuffle_right


@block
def ripple_multiplier(a, b):
    """
    a ripple multiplier, it's basically long addition in binary
    ripple adders aren't exactly efficient to start with but this is horriffically inefficient
    done like this an 8 bit multiplier requires 550 gates, 16 bit 2374 and 32 bit a massive 9862
    """

    # shuffle b right (least significant bit first) by every value between 0 and len(a) - 1
    shuffled = []
    for i in range(len(a)):
        shuffled.append(shuffle_right(b, i))
    shuffled_words, shuffled_carries = zip(*shuffled)

    # mask all the shuffled words by the associated line in b and sum them
    gated_words = []
    for line, word in zip(a, shuffled_words):
        gated_words.append([And(line, b) for b in word])
    total, sum_carry = ripple_sum(*gated_words)

    # mask all the carries from the shuffles by the associated line in b and or them all together with the sum carry
    gated_carries = []
    for line, carry in zip(a, shuffled_carries):
        gated_carries.append(And(line, carry))
    carry = Or(sum_carry, *gated_carries)

    return total, carry
