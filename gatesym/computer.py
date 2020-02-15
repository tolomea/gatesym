import collections

from gatesym.gates import Placeholder
from gatesym.utils import PlaceholderWord
from gatesym.modules import bus, cpu_core, math, memory, literals, jump

WORD_SIZE = 16
ROM_BASE = 0x000
ROM_SIZE = 8
LIT_BASE = 0x100
LIT_SIZE = 8
RAM_BASE = 0x200
RAM_SIZE = 8
ADD_BASE = 0x300
SUB_BASE = 0x304
MULT_BASE = 0x308
JUMP_BASE = 0x30C
SHR_BASE = 0x310
PRINT_BASE = 0x314
HALT_BASE = 0x315

Module = collections.namedtuple(
    "Module", "name base_address address_size data_lines write_line"
)


def computer(clock, rom_content):
    network = clock.network

    # cpu
    data_in = PlaceholderWord(network, WORD_SIZE)
    pc_in = PlaceholderWord(network, WORD_SIZE)
    pc_write = Placeholder(network)
    address, data_out, write_out = cpu_core.cpu_core(clock, data_in, pc_in, pc_write)

    # rom
    rom_write = Placeholder(network)
    rom_data = memory.rom(clock, rom_write, address, data_out, ROM_SIZE, rom_content)
    rom_module = Module("rom", ROM_BASE, ROM_SIZE, rom_data, rom_write)

    # add
    add_write = Placeholder(network)
    add_data = math.add(clock, add_write, address, data_out)
    add_module = Module("add", ADD_BASE, 2, add_data, add_write)

    # sub
    sub_write = Placeholder(network)
    sub_data = math.sub(clock, sub_write, address, data_out)
    sub_module = Module("sub", SUB_BASE, 2, sub_data, sub_write)

    # mult
    mult_write = Placeholder(network)
    mult_data = math.mult(clock, mult_write, address, data_out)
    mult_module = Module("mult", MULT_BASE, 2, mult_data, mult_write)

    # shift right
    shr_write = Placeholder(network)
    shr_data = math.shift_right(clock, shr_write, address, data_out)
    shr_module = Module("shr", SHR_BASE, 2, shr_data, shr_write)

    # lit
    low_literal_write = Placeholder(network)
    low_literal_data = literals.low_literal(
        clock, low_literal_write, address, data_out, LIT_SIZE
    )
    low_literal_module = Module(
        "lit", LIT_BASE, LIT_SIZE, low_literal_data, low_literal_write
    )

    # print
    print_write = Placeholder(network)
    print_data = memory.memory(clock, print_write, address, data_out, 0)
    print_module = Module("print", PRINT_BASE, 0, print_data, print_write)

    # ram
    ram_write = Placeholder(network)
    ram_data = memory.memory(clock, ram_write, address, data_out, RAM_SIZE)
    ram_module = Module("ram", RAM_BASE, RAM_SIZE, ram_data, ram_write)

    # jump
    jump_write = Placeholder(network)
    jump_data, _pc_in, _pc_write = jump.jump(clock, jump_write, address, data_out)
    pc_in.replace(_pc_in)
    pc_write.replace(_pc_write)
    jump_module = Module("jump", JUMP_BASE, 2, jump_data, jump_write)

    # halt, using memory is easy but a little overkill
    halt_write = Placeholder(network)
    halt_data = memory.memory(clock, halt_write, address, data_out, 0)
    halt_module = Module("halt", HALT_BASE, 0, halt_data, halt_write)

    modules = [
        rom_module,
        low_literal_module,
        ram_module,
        add_module,
        sub_module,
        mult_module,
        jump_module,
        print_module,
        shr_module,
        halt_module,
    ]

    # bus ties it all together
    module_data_lines = [
        (m.base_address, m.address_size, m.data_lines) for m in modules
    ]
    data_from_bus, write_lines = bus.bus(address, write_out, module_data_lines)
    data_in.replace(data_from_bus)
    for write_line, module in zip(write_lines, modules):
        module.write_line.replace(write_line)

    # print out the module sizes
    if 0:
        print("cpu", data_out[0].block.size)
        for module in modules:
            print(module.name, module.data_lines[0].block.size)
        print("bus", data_from_bus[0].block.size)
        print("total", network.get_size())

    return print_write, print_data, halt_write


# the addresses of all the fun stuff
# useful for remapping symbolic names to literal addresses in an assembler for example
symbols = dict(
    ADD_A=ADD_BASE,
    ADD_B=ADD_BASE + 1,
    ADD_R=ADD_BASE + 2,
    ADD_C=ADD_BASE + 3,
    SUB_A=SUB_BASE,
    SUB_B=SUB_BASE + 1,
    SUB_R=SUB_BASE + 2,
    SUB_C=SUB_BASE + 3,
    MULT_A=MULT_BASE,
    MULT_B=MULT_BASE + 1,
    MULT_R=MULT_BASE + 2,
    MULT_C=MULT_BASE + 3,
    PRINT=PRINT_BASE,
    JUMP=JUMP_BASE,
    JUMP_DEST=JUMP_BASE + 1,
    JUMP_IF_ZERO=JUMP_BASE + 2,
    JUMP_IF_NON_ZERO=JUMP_BASE + 3,
    SHR_A=SHR_BASE,
    SHR_R=SHR_BASE + 1,
    SHR_C=SHR_BASE + 2,
    _LIT=LIT_BASE,
    _RAM=RAM_BASE,
    HALT=HALT_BASE,
    INDIRECT=2 ** (WORD_SIZE - 1),
)
