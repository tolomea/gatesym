from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Placeholder, Switch
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
    rom_data = memory.rom(clock, rom_write, address, data_out, ROM_SIZE, rom_content)

    # add
    add_write = Placeholder(network)
    add_data = math.add(clock, add_write, address, data_out)

    # sub
    sub_write = Placeholder(network)
    sub_data = math.sub(clock, sub_write, address, data_out)

    # lit
    low_literal_write = Placeholder(network)
    low_literal_data = literals.low_literal(clock, low_literal_write, address, data_out, word_size // 2)

    # print
    print_write = Placeholder(network)
    print_data = memory.memory(clock, print_write, address, data_out, 0)

    # ram
    ram_write = Placeholder(network)
    ram_data = memory.memory(clock, ram_write, address, data_out, RAM_SIZE)

    # jump
    jump_write = Placeholder(network)
    jump_data, _pc_in, _pc_write = jump.jump(clock, jump_write, address, data_out)
    pc_in.replace(_pc_in)
    pc_write.replace(_pc_write)

    modules = [
        (ROM_BASE, ROM_SIZE, rom_data),
        (LIT_BASE, word_size // 2, low_literal_data),
        (RAM_BASE, RAM_SIZE, ram_data),
        (ADD_BASE, 2, add_data),
        (SUB_BASE, 2, sub_data),
        (PRINT_BASE, 0, print_data),
        (JUMP_BASE, 2, jump_data),
    ]

    data_from_bus, write_lines = bus.bus(address, write_out, modules)

    data_in.replace(data_from_bus)
    rom_write.replace(write_lines[0])
    low_literal_write.replace(write_lines[1])
    ram_write.replace(write_lines[2])
    add_write.replace(write_lines[3])
    sub_write.replace(write_lines[4])
    print_write.replace(write_lines[5])
    jump_write.replace(write_lines[6])

    return print_write, print_data


ROM_BASE = 0x000
ROM_SIZE = 8
LIT_BASE = 0x100
RAM_BASE = 0x200
RAM_SIZE = 8
ADD_BASE = 0x300
SUB_BASE = 0x304
JUMP_BASE = 0x308
PRINT_BASE = 0x30b

ADD_A = ADD_BASE
ADD_B = ADD_BASE + 1
ADD_R = ADD_BASE + 2
ADD_C = ADD_BASE + 3
SUB_A = SUB_BASE
SUB_B = SUB_BASE + 1
SUB_R = SUB_BASE + 2
SUB_C = SUB_BASE + 3
PRINT = PRINT_BASE
JUMP = JUMP_BASE
JUMP_DEST = JUMP_BASE + 1
JUMP_ZERO = JUMP_BASE + 2


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
    i = RAM_BASE
    return [
        LIT(1), ADD_B,
        ADD_R, ADD_A,
        i, ADD_B,
        ADD_R, i,
        i, PRINT,
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


def primes():
    i = RAM_BASE
    j = RAM_BASE + 1
    tmp = RAM_BASE + 2

    return assemble([
        LIT(3), i,
        "start:",
        LIT(3), j,
        "loop_start:",
        i, SUB_A,
        j, SUB_B,
        "loop_else", JUMP_DEST,
        SUB_R, JUMP_ZERO,

        i, tmp,
        j, SUB_B,
        "mod_loop:",
        tmp, SUB_A,
        SUB_R, tmp,
        "loop_end", JUMP_DEST,
        SUB_A, JUMP_ZERO,
        "mod_loop", JUMP_DEST,
        SUB_C, JUMP_ZERO,

        LIT(2), ADD_A,
        j, ADD_B,
        ADD_R, j,

        "loop_start", JUMP,
        "loop_else:",
        i, PRINT,
        "loop_end:",
        LIT(2), ADD_A,
        i, ADD_B,
        ADD_R, i,

        "start", JUMP,
    ])


def assemble(code):
    labels = {}
    i = 0
    for c in code:
        if isinstance(c, str) and c.endswith(":"):
            labels[c[:-1]] = i
        else:
            i += 1

    res = []
    for c in code:
        if isinstance(c, str):
            if not c.endswith(":"):
                res.append(LIT_BASE + labels[c])
        else:
            res.append(c)
    return res


def main():
    network = core.Network()
    clock = Switch(network)
    write, res = computer(clock, primes())

    print("size:", profiler.size(network))

    res = BinaryOut(res)
    network.drain()

    for i in range(20000):
        clock.write(True)
        network.drain()
        output = write.read()
        clock.write(False)
        network.drain()
        if output:
            print(res.read())
