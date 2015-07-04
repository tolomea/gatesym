from __future__ import unicode_literals, division, absolute_import

from gatesym.core import Network
from gatesym.gates import Tie
from gatesym.test_utils import BinaryIn, BinaryOut
from gatesym.modules.cpu_core import cpu_core


def test_basic():
    network = Network()
    clock = Tie(network)
    data_in = BinaryIn(network, 8)

    def step():
        network.drain()
        clock.write(True)
        network.drain()
        clock.write(False)
        network.drain()

    addr, data_out, write = cpu_core(clock, data_in)
    addr = BinaryOut(addr)
    data_out = BinaryOut(data_out)

    # fetch addr1 from pc
    network.drain()
    assert not write.read()
    assert addr.read() == 0
    data_in.write(100)

    # fetch data from addr1
    step()
    assert not write.read()
    assert addr.read() == 100
    data_in.write(101)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 1
    data_in.write(102)

    # write data to addr2
    step()
    assert write.read()
    assert addr.read() == 102
    assert data_out.read() == 101

    # fetch addr1 from pc
    step()
    assert not write.read()
    assert addr.read() == 2
    data_in.write(99)

    # fetch data from addr1
    step()
    assert not write.read()
    assert addr.read() == 99
    data_in.write(98)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 3
    data_in.write(97)

    # write data to addr2
    step()
    assert write.read()
    assert addr.read() == 97
    assert data_out.read() == 98
