from __future__ import unicode_literals, division, absolute_import

import random

from gatesym import core, gates, test_utils
from gatesym.modules import memory


def test_memory():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 8)
    data_in = test_utils.BinaryIn(network, 8)
    mem = memory.memory(clock, write_flag, address, data_in, 4)
    data_out = test_utils.BinaryOut(mem)
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

    data = [0] * 8
    for i in range(16):
        v = random.randrange(256)
        a = random.randrange(8)
        write(v, a)
        data[a] = v

        a = random.randrange(8)
        assert read(a) == data[a]


def test_rom():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 8)
    data_in = test_utils.BinaryIn(network, 8)
    data = [random.randrange(256) for i in range(16)]
    rom = memory.rom(clock, write_flag, address, data_in, 4, data)
    data_out = test_utils.BinaryOut(rom)
    network.drain()

    def read(addr):
        address.write(addr)
        write_flag.write(0)
        network.drain()
        return data_out.read()

    for i in range(100):
        a = random.randrange(16)
        assert read(a) == data[a]
