from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import block


@block
def jump(clock, write, address, data_in):
    return data_in, data_in, write
