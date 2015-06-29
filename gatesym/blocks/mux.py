from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import And, Or, Not, block


@block
def address_decode(address):
    control_lines = []
    for i in range(2**len(address)):
        addr_lines = []
        for j, line in enumerate(address):
            if i & 2**j:
                addr_lines.append(line)
            else:
                addr_lines.append(Not(line))
        control_lines.append(And(*addr_lines))
    return control_lines


@block
def bit_switch(control_lines, *data):
    assert len(control_lines) >= len(data)
    return Or(*[And(c, d) for c, d in zip(control_lines, data)])


@block
def bit_mux(address, *data):
    assert 2**len(address) >= len(data)
    control_lines = address_decode(address)
    return bit_switch(control_lines, *data)


@block
def word_switch(control_lines, *data):
    output = []
    for data_lines in zip(*data):
        output.append(bit_switch(control_lines, *data_lines))
    return output


@block
def word_mux(address, *data):
    control_lines = address_decode(address)
    return word_switch(control_lines, *data)
