from gatesym.gates import block, And
from gatesym.blocks.mux import word_switch, address_matches


@block
def bus(address, write, modules):
    """
    the bus switches the write line between the modules and muxes the data lines coming back
    in both cases based on the address lines
    """

    # the control line for each module is based on the relevant address prefix match
    control_lines = []
    for prefix, size, data_in in modules:
        prefix //= 2**size
        control_lines.append(address_matches(prefix, address[size:]))

    # switch the data and write lines based on the control lines
    data_out = word_switch(control_lines, *[d for p, s, d in modules])
    write_lines = [And(write, ctrl) for ctrl in control_lines]

    return data_out, write_lines
