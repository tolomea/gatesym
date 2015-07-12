from __future__ import unicode_literals, division, absolute_import

from gatesym.core import Network
from gatesym.gates import Switch, Placeholder, And
from gatesym.test_utils import BinaryIn, BinaryOut
from gatesym.modules.cpu_core import cpu_core
from gatesym.utils import PlaceholderWord
from gatesym.blocks import mux


def test_basic():
    network = Network()
    clock = Switch(network)
    data_in = BinaryIn(network, 8)
    write_pc = Switch(network)
    pc_in = BinaryIn(network, 8)

    def step():
        network.drain()
        clock.write(True)
        network.drain()
        clock.write(False)
        network.drain()

    addr, data_out, write = cpu_core(clock, data_in, pc_in, write_pc)
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


def test_jmp():
    """ twiddle the bits manually """
    network = Network()
    clock = Switch(network)
    data_in = BinaryIn(network, 8)
    pc_in = BinaryIn(network, 8)
    write_pc = Switch(network)

    def step():
        network.drain()
        clock.write(True)
        network.drain()
        clock.write(False)
        network.drain()

    addr, data_out, write = cpu_core(clock, data_in, pc_in, write_pc)

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
    data_in.write(200)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 1
    data_in.write(102)
    pc_in.write(200)
    write_pc.write(True)

    # write data to addr2 AND PC
    step()
    assert write.read()
    assert addr.read() == 102
    assert data_out.read() == 200

    # fetch addr1 from pc
    step()
    assert not write.read()
    assert addr.read() == 200
    write_pc.write(False)
    data_in.write(99)

    # fetch data from addr1
    step()
    assert not write.read()
    assert addr.read() == 99
    data_in.write(98)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 201
    data_in.write(97)

    # write data to addr2
    step()
    assert write.read()
    assert addr.read() == 97
    assert data_out.read() == 98


def test_jmp2():
    """ same deal as above but with automatic signals so more realistic timing """
    network = Network()
    clock = Switch(network)
    data_in = BinaryIn(network, 8)
    pc_in = PlaceholderWord(network, 8)
    write_pc = Placeholder(network)

    def step():
        network.drain()
        clock.write(True)
        network.drain()
        clock.write(False)
        network.drain()

    addr, data_out, write = cpu_core(clock, data_in, pc_in, write_pc)
    write_pc = write_pc.replace(And(write, mux.equals(102, addr)))
    pc_in = pc_in.replace(data_out)

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
    data_in.write(200)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 1
    data_in.write(102)

    # write data to addr2 AND PC
    step()
    assert write.read()
    assert addr.read() == 102
    assert data_out.read() == 200

    # fetch addr1 from pc
    step()
    assert not write.read()
    assert addr.read() == 200
    data_in.write(99)

    # fetch data from addr1
    step()
    assert not write.read()
    assert addr.read() == 99
    data_in.write(98)

    # fetch addr2 from pc
    step()
    assert not write.read()
    assert addr.read() == 201
    data_in.write(97)

    # write data to addr2
    step()
    assert write.read()
    assert addr.read() == 97
    assert data_out.read() == 98
