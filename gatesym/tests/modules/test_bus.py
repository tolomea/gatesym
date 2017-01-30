from gatesym.core import Network
from gatesym.gates import Switch
from gatesym.test_utils import BinaryIn, BinaryOut
from gatesym.modules.bus import bus


def test_basic():
    network = Network()
    address = BinaryIn(network, 8)
    write = Switch(network)
    m1_data = BinaryIn(network, 8, 100)
    m2_data = BinaryIn(network, 8, 200)
    modules = [
        (0, 3, m1_data),
        (8, 2, m2_data),
    ]
    data, (m1_write, m2_write) = bus(address, write, modules)
    data = BinaryOut(data)

    network.drain()
    assert data.read() == 100
    assert not m1_write.read()
    assert not m2_write.read()

    write.write(True)
    network.drain()
    assert data.read() == 100
    assert m1_write.read()
    assert not m2_write.read()

    write.write(False)
    address.write(9)
    network.drain()
    assert data.read() == 200
    assert not m1_write.read()
    assert not m2_write.read()

    write.write(True)
    network.drain()
    assert data.read() == 200
    assert not m1_write.read()
    assert m2_write.read()
