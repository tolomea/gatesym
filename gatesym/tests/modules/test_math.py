import random

from gatesym import core, gates, test_utils
from gatesym.modules import math


class Helper(object):

    def __init__(self, module_func):
        self.network = core.Network()
        self.clock = gates.Switch(self.network)
        self.write_flag = gates.Switch(self.network)
        self.address = test_utils.BinaryIn(self.network, 3)
        self.data_in = test_utils.BinaryIn(self.network, 8)
        module = module_func(self.clock, self.write_flag, self.address, self.data_in)
        self.data_out = test_utils.BinaryOut(module)
        self.network.drain()

    def write(self, value, addr):
        self.data_in.write(value)
        self.address.write(addr)
        self.write_flag.write(1)
        self.clock.write(1)
        self.network.drain()
        self.clock.write(0)
        self.network.drain()
        self.write_flag.write(0)

    def read(self, addr):
        self.address.write(addr)
        self.write_flag.write(0)
        self.network.drain()
        return self.data_out.read()


def test_adder():
    helper = Helper(math.add)

    for i in range(10):
        v1 = random.randrange(256)
        helper.write(v1, 0)
        assert helper.read(0) == v1

        v2 = random.randrange(256)
        helper.write(v2, 1)
        assert helper.read(1) == v2

        res = helper.read(2)
        assert res == (v1 + v2) % 256
        res = helper.read(3)
        assert res == (v1 + v2) // 256


def test_subtractor():
    helper = Helper(math.sub)

    for i in range(10):
        v1 = random.randrange(256)
        helper.write(v1, 0)
        assert helper.read(0) == v1

        v2 = random.randrange(256)
        helper.write(v2, 1)
        assert helper.read(1) == v2

        res = helper.read(2)
        assert res == (v1 - v2) % 256
        res = helper.read(3)
        assert res == (v1 < v2)


def test_multiplier():
    helper = Helper(math.mult)

    for i in range(10):
        v1 = random.randrange(256)
        helper.write(v1, 0)
        assert helper.read(0) == v1

        v2 = random.randrange(256)
        helper.write(v2, 1)
        assert helper.read(1) == v2

        res = helper.read(2)
        assert res == (v1 * v2) % 256
        res = helper.read(3)
        assert res == ((v1 * v2) > 255)


def test_compact_adder():
    helper = Helper(math.compact_add)

    for i in range(10):
        v1 = random.randrange(256)
        helper.write(v1, 0)

        v2 = random.randrange(256)
        helper.write(v2, 1)

        res = helper.read(0)
        assert res == (v1 + v2) % 256
        res = helper.read(1)
        assert res == (v1 + v2) // 256


def test_combined():
    helper = Helper(math.combined)

    for i in range(10):
        v1 = random.randrange(256)
        helper.write(v1, 0)
        assert helper.read(0) == v1

        v2 = random.randrange(256)
        helper.write(v2, 1)
        assert helper.read(1) == v2

        res = helper.read(2)
        assert res == (v1 + v2) % 256
        res = helper.read(3)
        assert res == (v1 + v2) // 256

        res = helper.read(4)
        assert res == (v1 - v2) % 256
        res = helper.read(5)
        assert res == (v1 < v2)
