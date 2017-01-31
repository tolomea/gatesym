import pytest

from gatesym import core


def test_tie():
    network = core.Network()
    idx = network.add_gate(core.TIE)
    assert network.read(idx) is False
    network.write(idx, True)
    assert network.read(idx) is True
    network.write(idx, False)
    assert network.read(idx) is False


def test_switch():
    network = core.Network()
    idx = network.add_gate(core.SWITCH)
    assert network.read(idx) is False
    network.write(idx, True)
    assert network.read(idx) is True
    network.write(idx, False)
    assert network.read(idx) is False


def test_0_and():
    network = core.Network()
    idx = network.add_gate(core.AND)

    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is True


@pytest.mark.parametrize("input_type", [core.SWITCH, core.TIE])
def test_1_and(input_type):
    network = core.Network()
    a_idx = network.add_gate(input_type)
    idx = network.add_gate(core.AND)
    network.add_link(a_idx, idx)

    network.write(a_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, True)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False


@pytest.mark.parametrize("input_type", [core.SWITCH, core.TIE])
def test_2_and(input_type):
    network = core.Network()
    a_idx = network.add_gate(input_type)
    b_idx = network.add_gate(input_type)
    idx = network.add_gate(core.AND)
    network.add_link(a_idx, idx)
    network.add_link(b_idx, idx, True)

    network.write(a_idx, False)
    network.write(b_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, True)
    network.write(b_idx, False)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, False)
    network.write(b_idx, True)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, True)
    network.write(b_idx, True)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, False)
    network.write(b_idx, False)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is False


def test_0_or():
    network = core.Network()
    idx = network.add_gate(core.OR)

    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is False


@pytest.mark.parametrize("input_type", [core.SWITCH, core.TIE])
def test_1_or(input_type):
    network = core.Network()
    a_idx = network.add_gate(input_type)
    idx = network.add_gate(core.OR)
    network.add_link(a_idx, idx)

    network.write(a_idx, False)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, True)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False


@pytest.mark.parametrize("input_type", [core.SWITCH, core.TIE])
def test_2_or(input_type):
    network = core.Network()
    a_idx = network.add_gate(input_type)
    b_idx = network.add_gate(input_type)
    idx = network.add_gate(core.OR)
    network.add_link(a_idx, idx)
    network.add_link(b_idx, idx, True)

    network.write(a_idx, False)
    network.write(b_idx, False)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, True)
    network.write(b_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, False)
    network.write(b_idx, True)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is False

    network.write(a_idx, True)
    network.write(b_idx, True)
    assert network.read(idx) is False
    network.step()
    assert network.read(idx) is True

    network.write(a_idx, False)
    network.write(b_idx, False)
    assert network.read(idx) is True
    network.step()
    assert network.read(idx) is True


def test_step():
    network = core.Network()
    idx_0 = network.add_gate(core.SWITCH)
    idx_1 = network.add_gate(core.AND)
    idx_2 = network.add_gate(core.AND)
    network.add_link(idx_0, idx_1)
    network.add_link(idx_1, idx_2)

    network.drain()
    assert network.read(idx_0) is False
    assert network.read(idx_1) is False
    assert network.read(idx_2) is False

    network.write(idx_0, True)
    assert network.read(idx_0) is True
    assert network.read(idx_1) is False
    assert network.read(idx_2) is False

    assert network.step() is True
    assert network.read(idx_0) is True
    assert network.read(idx_1) is True
    assert network.read(idx_2) is False

    assert network.step() is False
    assert network.read(idx_0) is True
    assert network.read(idx_1) is True
    assert network.read(idx_2) is True

    assert network.step() is False
    assert network.read(idx_0) is True
    assert network.read(idx_1) is True
    assert network.read(idx_2) is True


def test_drain():
    network = core.Network()
    idx_0 = network.add_gate(core.SWITCH)
    idx_1 = network.add_gate(core.AND)
    idx_2 = network.add_gate(core.AND)
    network.add_link(idx_0, idx_1)
    network.add_link(idx_1, idx_2)

    network.drain()
    assert network.read(idx_0) is False
    assert network.read(idx_1) is False
    assert network.read(idx_2) is False

    network.write(idx_0, True)
    assert network.read(idx_0) is True
    assert network.read(idx_1) is False
    assert network.read(idx_2) is False

    assert network.drain() == 2
    assert network.read(idx_0) is True
    assert network.read(idx_1) is True
    assert network.read(idx_2) is True

    network.write(idx_0, True)
    assert network.drain() == 0

    network.write(idx_0, False)
    network.write(idx_0, True)
    assert network.drain() == 1
