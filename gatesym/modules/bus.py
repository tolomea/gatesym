from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block, And
from gatesym.blocks.mux import word_switch, equals


@block
def bus(address, write, modules):
    control_lines = []
    for prefix, size, data_in in modules:
        prefix //= 2**size
        control_lines.append(equals(prefix, address[size:]))
    data_out = word_switch(control_lines, *[d for p, s, d in modules])
    write_lines = [And(write, ctrl) for ctrl in control_lines]
    return data_out, write_lines
