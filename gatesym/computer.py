from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Placeholder
from gatesym.utils import PlaceholderWord
from gatesym.modules import bus, cpu_core, math, memory, literals, jump

WORD_SIZE = 16
ROM_BASE = 0x000
ROM_SIZE = 8
LIT_BASE = 0x100
RAM_BASE = 0x200
RAM_SIZE = 8
ADD_BASE = 0x300
SUB_BASE = 0x304
JUMP_BASE = 0x308
PRINT_BASE = 0x30b


def computer(clock, rom_content):
    network = clock.network
    data_in = PlaceholderWord(network, WORD_SIZE)
    pc_in = PlaceholderWord(network, WORD_SIZE)
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
    low_literal_data = literals.low_literal(clock, low_literal_write, address, data_out, WORD_SIZE // 2)

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
        (LIT_BASE, WORD_SIZE // 2, low_literal_data),
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


symbols = dict(
    ADD_A=ADD_BASE,
    ADD_B=ADD_BASE + 1,
    ADD_R=ADD_BASE + 2,
    ADD_C=ADD_BASE + 3,
    SUB_A=SUB_BASE,
    SUB_B=SUB_BASE + 1,
    SUB_R=SUB_BASE + 2,
    SUB_C=SUB_BASE + 3,
    PRINT=PRINT_BASE,
    JUMP=JUMP_BASE,
    JUMP_DEST=JUMP_BASE + 1,
    JUMP_ZERO=JUMP_BASE + 2,
    _LIT=LIT_BASE,
    _RAM=RAM_BASE,
)
