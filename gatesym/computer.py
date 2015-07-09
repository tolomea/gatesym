from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Placeholder, Tie
from gatesym.utils import PlaceholderWord
from gatesym.modules import bus, cpu_core, math, memory, literals, jump
from gatesym import core, profiler
from gatesym.test_utils import BinaryOut


def computer(clock, rom_content):
    word_size = 16
    network = clock.network
    data_in = PlaceholderWord(network, word_size)
    pc_in = PlaceholderWord(network, word_size)
    pc_write = Placeholder(network)

    address, data_out, write_out = cpu_core.cpu_core(clock, data_in, pc_in, pc_write)

    # rom
    rom_write = Placeholder(network)
    rom_size = 8
    rom_data = memory.rom(clock, rom_write, address, data_out, rom_size, rom_content)

    # add
    adder_write = Placeholder(network)
    adder_data = math.add(clock, adder_write, address, data_out)

    # lit
    low_literal_write = Placeholder(network)
    low_literal_data = literals.low_literal(clock, low_literal_write, address, data_out, word_size // 2)

    # print
    print_write = Placeholder(network)
    print_data = memory.memory(clock, print_write, address, data_out, 0)

    # ram
    ram_write = Placeholder(network)
    ram_data = memory.memory(clock, ram_write, address, data_out, word_size // 2)

    # jump
    jump_write = Placeholder(network)
    jump_data, _pc_in, _pc_write = jump.jump(clock, jump_write, address, data_out)
    pc_in.replace(_pc_in)
    pc_write.replace(_pc_write)

    modules = [
        (ROM_BASE, word_size // 2, rom_data),
        (LIT_BASE, word_size // 2, low_literal_data),
        (RAM_BASE, word_size // 2, ram_data),
        (ADD_BASE, 2, adder_data),
        (PRINT_BASE, 0, print_data),
        (JUMP_BASE, 0, jump_data),
    ]

    data_from_bus, write_lines = bus.bus(address, write_out, modules)

    data_in.replace(data_from_bus)
    rom_write.replace(write_lines[0])
    low_literal_write.replace(write_lines[1])
    ram_write.replace(write_lines[2])
    adder_write.replace(write_lines[3])
    print_write.replace(write_lines[4])
    jump_write.replace(write_lines[5])

    return print_write, print_data


ROM_BASE = 0x000
LIT_BASE = 0x100
RAM_BASE = 0x200
ADD_BASE = 0x300
JUMP_BASE = 0x304
PRINT_BASE = 0x305

ADD_A = ADD_BASE
ADD_B = ADD_BASE + 1
ADD_R = ADD_BASE + 2
PRINT = PRINT_BASE
JUMP = JUMP_BASE


def LIT(x):
    return LIT_BASE + x


def basic_add():
    return [
        LIT(123), ADD_A,
        LIT(5), ADD_B,
        ADD_R, ADD_A,
        LIT(67), ADD_B,
        ADD_R, PRINT,
    ]


def loop():
    return [
        LIT(1), ADD_B,
        ADD_R, ADD_A,
        PRINT, ADD_B,
        ADD_R, PRINT,
        LIT(0), JUMP,
    ]


def fib():
    return assemble([
        LIT(0), ADD_A,
        LIT(1), ADD_B,
        LIT(1), PRINT,
        "loop:",
        ADD_R, PRINT,
        ADD_R, ADD_A,
        ADD_R, PRINT,
        ADD_R, ADD_B,
        "loop", JUMP,
    ])


def assemble(code):
    labels = {}
    i = 0
    for c in code:
        if isinstance(c, basestring) and c.endswith(":"):
            labels[c[:-1]] = i
        else:
            i += 1

    res = []
    for c in code:
        if isinstance(c, basestring):
            if not c.endswith(":"):
                res.append(LIT_BASE + labels[c])
        else:
            res.append(c)
    return res


def main():
    network = core.Network()
    clock = Tie(network)
    write, res = computer(clock, fib())

    print "size:", profiler.size(network)

    res = BinaryOut(res)
    network.drain()

    for i in range(200):
        clock.write(True)
        network.drain()
        output = write.read()
        clock.write(False)
        network.drain()
        if output:
            print res.read()
