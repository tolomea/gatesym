from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, test_utils
from gatesym.blocks import multipliers


def test_ripple_multiplier():
    network = core.Network()
    a = test_utils.BinaryIn(network, 8)
    b = test_utils.BinaryIn(network, 8)
    r, c = multipliers.ripple_multiplier(a, b)
    r = test_utils.BinaryOut(r)

    for i in range(10):
        v1 = random.randrange(32)
        v2 = random.randrange(32)
        print v1, v2
        a.write(v1)
        b.write(v2)
        network.drain()
        assert c.read() == (v1 * v2 >= 256)
        assert r.read() == (v1 * v2) % 256
