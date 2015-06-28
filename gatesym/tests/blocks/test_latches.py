from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, utils
from gatesym.blocks import latches


def test_ms_d_flop_basic():
    network = core.Network()
    clock = gates.Tie(network)
    data = gates.Tie(network)
    flop = latches.ms_d_flop(data, clock)
    network.drain()

    # clock a 1 through
    data.write(True)
    network.drain()
    assert not flop.read()
    clock.write(True)
    network.drain()
    assert not flop.read()
    clock.write(False)
    network.drain()
    assert flop.read()

    # and back to 0
    data.write(False)
    network.drain()
    assert flop.read()
    clock.write(True)
    network.drain()
    assert flop.read()
    clock.write(False)
    network.drain()
    assert not flop.read()


def test_ms_d_flop_timing():
    network = core.Network()
    clock = gates.Tie(network)
    data = gates.Tie(network)
    flop = latches.ms_d_flop(data, clock)
    network.drain()

    # clock a 1 through
    data.write(True)
    network.drain()
    assert not flop.read()
    clock.write(True)
    network.drain()
    assert not flop.read()
    clock.write(False)
    data.write(False)
    network.drain()
    assert flop.read()

    # and back to 0
    data.write(False)
    network.drain()
    assert flop.read()
    clock.write(True)
    network.drain()
    assert flop.read()
    clock.write(False)
    data.write(True)
    network.drain()
    assert not flop.read()


def test_register():
    network = core.Network()
    clock = gates.Tie(network)
    data = utils.BinaryIn(network, 8)
    register = latches.register(data, clock)
    res = utils.BinaryOut(register)
    network.drain()

    # clock a value through
    v1 = random.randrange(256)
    data.write(v1)
    network.drain()
    assert res.read() == 0
    clock.write(True)
    network.drain()
    assert res.read() == 0
    clock.write(False)
    network.drain()
    assert res.read() == v1

    # and a different value
    v2 = random.randrange(256)
    data.write(v2)
    network.drain()
    assert res.read() == v1
    clock.write(True)
    network.drain()
    assert res.read() == v1
    clock.write(False)
    network.drain()
    assert res.read() == v2
