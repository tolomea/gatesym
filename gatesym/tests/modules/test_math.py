from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, utils
from gatesym.modules import math


def test_adder_adding():
    network = core.Network()
    clock = gates.Tie(network)
    write_flag = gates.Tie(network)
    address = utils.BinaryIn(network, 2)
    data_in = utils.BinaryIn(network, 8)
    adder = math.add(clock, write_flag, address, data_in)
    data_out = utils.BinaryOut(adder)
    network.drain()

    def write(value, addr):
        data_in.write(value)
        address.write(addr)
        write_flag.write(1)
        clock.write(1)
        network.drain()
        clock.write(0)
        network.drain()
        write_flag.write(0)

    def read(addr):
        address.write(addr)
        write_flag.write(0)
        network.drain()
        return data_out.read()

    for i in range(10):
        v1 = random.randrange(256)
        write(v1, 0)
        assert read(0) == v1

        v2 = random.randrange(256)
        write(v2, 1)
        assert read(1) == v2

        print v1, v2

        res = read(2)
        assert res == (v1 + v2) % 256
        res = read(3)
        assert res == (v1 + v2) // 256

        # and another
        v1 = random.randrange(256)
        write(v1, 0)
        assert read(0) == v1

        v2 = random.randrange(256)
        write(v2, 1)
        assert read(1) == v2

        res = read(2)
        assert res == (v1 + v2) % 256
        res = read(3)
        assert res == (v1 + v2) // 256
