import pytest

from gatesym import core, test_utils
from gatesym.blocks import mux


@pytest.mark.parametrize(
    "addr,a,b,c,d",
    [
        (0, True, False, False, False),
        (1, False, True, False, False),
        (2, False, False, True, False),
        (3, False, False, False, True),
    ],
)
def test_address_decode(addr, a, b, c, d):
    network = core.Network()
    address = test_utils.BinaryIn(network, 2)
    control_lines = mux.address_decode(address)

    address.write(addr)
    network.drain()
    assert control_lines[0].read() == a
    assert control_lines[1].read() == b
    assert control_lines[2].read() == c
    assert control_lines[3].read() == d


def test_bit_mux():
    network = core.Network()
    lines = test_utils.BinaryIn(network, 3)
    data_lines = [lines[0], lines[1]]
    address = [lines[2]]
    res = mux.bit_mux(address, *data_lines)

    for i in range(8):
        lines.write(i)
        network.drain()
        if i in {1, 3, 6, 7}:
            assert res.read()
        else:
            assert not res.read()


def test_word_mux():
    network = core.Network()
    inputs = [test_utils.BinaryIn(network, 2, value=3 - i) for i in range(4)]
    address = test_utils.BinaryIn(network, 2)
    m = mux.word_mux(address, *inputs)
    res = test_utils.BinaryOut(m)

    for i in range(4):
        address.write(i)
        network.drain()
        assert res.read() == 3 - i
