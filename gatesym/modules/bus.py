from gatesym.gates import block, And
from gatesym.blocks.mux import word_switch, address_matches


@block
def bus(address, write, modules):
    """
    the bus switches the write line between the modules and muxes the data lines coming back
    in both cases based on the address lines
    """

    # module prefixes are aligned to their sizes
    for prefix, size, data_in in modules:
        assert prefix % 2 ** size == 0, (prefix, size)

    # module ranges don't overlap
    _modules = sorted(modules)
    for a, b in zip(_modules, _modules[1:]):
        a_start, a_size, _ = a
        b_start, b_size, _ = b
        a_end = a_start + 2 ** a_size - 1
        assert a_end < b_start

    # the control line for each module is based on the relevant address prefix match
    control_lines = []
    for prefix, size, data_in in modules:
        prefix //= 2 ** size
        control_lines.append(address_matches(prefix, address[size:]))

    # switch the data and write lines based on the control lines
    data_out = word_switch(control_lines, *[d for p, s, d in modules])
    write_lines = [And(write, ctrl) for ctrl in control_lines]

    return data_out, write_lines
