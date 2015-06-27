from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import networks as adders
from gatesym import gatesym


def test_half_adder():
    network = gatesym.Network()
    a = gatesym.Tie(network)
    b = gatesym.Tie(network)
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
    network = gatesym.Network()
    a = gatesym.Tie(network)
    b = gatesym.Tie(network)
    c = gatesym.Tie(network)
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
    network = gatesym.Network()
    a = gatesym.BinaryIn(network, 8)
    b = gatesym.BinaryIn(network, 8)
    r, c = adders.ripple_adder(a, b)
    r = gatesym.BinaryOut(r)

    for i in range(10):
        v1 = random.randrange(256)
        v2 = random.randrange(256)
        print v1, v2
        a.write(v1)
        b.write(v2)
        network.drain()
        assert c.read() == (v1 + v2 >= 256)
        assert r.read() == (v1 + v2) % 256
