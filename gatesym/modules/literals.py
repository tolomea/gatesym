from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Tie, block


@block
def low_literal(clock, write, address, data_in):
    data_out = []
    data_out.extend(address)
    for i in range(len(data_in) - len(address)):
        data_out.append(Tie(clock.network))
    return data_out


@block
def high_literal(clock, write, address, data_in):
    data_out = []
    for i in range(len(data_in) - len(address)):
        data_out.append(Tie(clock.network))
    data_out.extend(address)
    return data_out
