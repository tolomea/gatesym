from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Placeholder, Tie
from gatesym.utils import PlaceholderWord
from gatesym.modules import bus, cpu_core, math, memory, literals
from gatesym import core
from gatesym.test_utils import BinaryOut


def computer(clock):
    word_size = 16
    network = clock.network
    data_in = PlaceholderWord(network, word_size)

    address, data_out, write_out = cpu_core.cpu_core(clock, data_in)

    rom_write = Placeholder(network)
    rom_size = 8
    rom_content = [
        0x17a, 0x200,
        0x105, 0x201,
        0x202, 0x200,
        0x143, 0x201,
        0x202, 0x300,
    ]
    rom_data = memory.rom(clock, rom_write, address, data_out, rom_size, rom_content)

    adder_write = Placeholder(network)
    adder_data = math.add(clock, adder_write, address, data_out)

    low_literal_write = Placeholder(network)
    low_literal_data = literals.low_literal(clock, low_literal_write, address, data_out, word_size // 2)

    ram_write = Placeholder(network)
    ram_data = memory.memory(clock, ram_write, address, data_out, 0)

    modules = [
        (0, rom_size, rom_data),
        (0x100, word_size // 2, low_literal_data),
        (0x200, 2, adder_data),
        (0x300, 0, ram_data),
    ]

    data_from_bus, write_lines = bus.bus(address, write_out, modules)

    data_in = data_in.replace(data_from_bus)
    rom_write = rom_write.replace(write_lines[0])
    low_literal_write = low_literal_write.replace(write_lines[1])
    adder_write = adder_write.replace(write_lines[2])
    ram_write = ram_write.replace(write_lines[3])

    return ram_write, ram_data


def main():
    network = core.Network()
    clock = Tie(network)
    write, res = computer(clock)
    res = BinaryOut(res)
    network.drain()

    for i in range(100):
        clock.write(True)
        network.drain()
        output = write.read()
        clock.write(False)
        network.drain()
        if output:
            print res.read()
