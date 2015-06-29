from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, test_utils
from gatesym.modules import literals


def test_low_literal():
    network = core.Network()
    clock = gates.Tie(network)
    write = gates.Tie(network)
    data_in = test_utils.BinaryIn(network, 8)
    address = test_utils.BinaryIn(network, 4)
    low_literal = literals.low_literal(clock, write, address, data_in)
    data_out = test_utils.BinaryOut(low_literal)

    # read a value
    v = random.randrange(16)
    address.write(v)
    assert data_out.read() == v

    # and another
    v = random.randrange(16)
    address.write(v)
    assert data_out.read() == v


def test_high_literal():
    network = core.Network()
    clock = gates.Tie(network)
    write = gates.Tie(network)
    data_in = test_utils.BinaryIn(network, 8)
    address = test_utils.BinaryIn(network, 4)
    low_literal = literals.high_literal(clock, write, address, data_in)
    data_out = test_utils.BinaryOut(low_literal)

    # read a value
    v = random.randrange(16)
    address.write(v)
    assert data_out.read() == v << 4

    # and another
    v = random.randrange(16)
    address.write(v)
    assert data_out.read() == v << 4
