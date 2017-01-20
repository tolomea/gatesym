from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, test_utils
from gatesym.blocks import adders


def test_half_adder():
    network = core.Network()
    a = gates.Switch(network)
    b = gates.Switch(network)
    r, c = adders.half_adder(a, b)
    network.drain()

    a.write(False)
    b.write(False)
    network.drain()
    assert not r.read()
    assert not c.read()

    a.write(True)
    b.write(False)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(False)
    b.write(True)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(True)
    b.write(True)
    network.drain()
    assert not r.read()
    assert c.read()


def test_full_adder():
    network = core.Network()
    a = gates.Switch(network)
    b = gates.Switch(network)
    c = gates.Switch(network)
    r, co = adders.full_adder(a, b, c)
    network.drain()

    a.write(False)
    b.write(False)
    c.write(False)
    network.drain()
    assert not r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(False)
    b.write(True)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(True)
    c.write(False)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(False)
    c.write(True)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(True)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(True)
    b.write(True)
    c.write(True)
    network.drain()
    assert r.read()
    assert co.read()


def test_ripple_adder():
    network = core.Network()
    a = test_utils.BinaryIn(network, 8)
    b = test_utils.BinaryIn(network, 8)
    r, c = adders.ripple_adder(a, b)
    r = test_utils.BinaryOut(r)

    for i in range(10):
        v1 = random.randrange(256)
        v2 = random.randrange(256)
        print(v1, v2)
        a.write(v1)
        b.write(v2)
        network.drain()
        assert c.read() == (v1 + v2 >= 256)
        assert r.read() == (v1 + v2) % 256


def test_ripple_incr():
    network = core.Network()
    a = test_utils.BinaryIn(network, 8)
    r, c = adders.ripple_incr(a)
    r = test_utils.BinaryOut(r)

    for i in range(10):
        v = random.randrange(255)
        print(v)
        a.write(v)
        network.drain()
        assert c.read() == 0
        assert r.read() == v + 1

    a.write(255)
    network.drain()
    assert c.read() == 1
    assert r.read() == 0


def test_ripple_sum():
    count = random.randrange(2, 10)

    network = core.Network()
    inputs = [test_utils.BinaryIn(network, 8) for i in range(count)]
    res, carry = adders.ripple_sum(*inputs)
    res = test_utils.BinaryOut(res)

    for i in range(10):
        values = [random.randrange(512 // count) for i in range(count)]
        print(values)
        for i, v in zip(inputs, values):
            i.write(v)
        network.drain()
        assert carry.read() == (sum(values) >= 256)
        assert res.read() == (sum(values) % 256)


def test_ripple_subtractor():
    network = core.Network()
    a = test_utils.BinaryIn(network, 8)
    b = test_utils.BinaryIn(network, 8)
    r, c = adders.ripple_subtractor(a, b)
    r = test_utils.BinaryOut(r)

    for i in range(10):
        v1 = random.randrange(256)
        v2 = random.randrange(256)
        print(v1, v2)
        a.write(v1)
        b.write(v2)
        network.drain()
        assert c.read() == (v1 < v2)
        assert r.read() == (v1 - v2) % 256
