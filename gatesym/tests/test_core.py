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


def test_merge():
    # two switches both feeding to two 2 input and's
    # both of which feed to it's own 1 input or's
    # and an extra negated 1 input or hanging off the first and
    network = core.Network()
    switch_1 = network.add_gate(core.SWITCH)
    switch_2 = network.add_gate(core.SWITCH)
    and_1 = network.add_gate(core.AND)
    or_1 = network.add_gate(core.OR)
    network.add_link(switch_1, and_1)
    network.add_link(switch_2, and_1, True)
    network.add_link(and_1, or_1)
    and_2 = network.add_gate(core.AND)
    or_2 = network.add_gate(core.OR)
    network.add_link(switch_1, and_2)
    network.add_link(switch_2, and_2, True)
    network.add_link(and_2, or_2)
    or_3 = network.add_gate(core.OR)
    network.add_link(and_1, or_3, True)

    # toggle the switches and check that the 1 input and's do the right thing
    def check_behaviour():
        network.write(switch_1, False)
        network.write(switch_2, False)
        network.drain()
        assert network.read(or_1) is False
        assert network.read(or_2) is False
        assert network.read(or_3) is True

        network.write(switch_1, True)
        network.write(switch_2, False)
        network.drain()
        assert network.read(or_1) is True
        assert network.read(or_2) is True
        assert network.read(or_3) is False

        network.write(switch_1, False)
        network.write(switch_2, True)
        network.drain()
        assert network.read(or_1) is False
        assert network.read(or_2) is False
        assert network.read(or_3) is True

        network.write(switch_1, True)
        network.write(switch_2, True)
        network.drain()
        assert network.read(or_1) is False
        assert network.read(or_2) is False
        assert network.read(or_3) is True

    # baseline
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 2, core.OR: 3}
    assert stats["aliases_by_type"] == {}
    assert stats["size"] == 7
    check_behaviour()

    # can't merge the first 2 ors
    with pytest.raises(AssertionError):
        network.merge(or_1, or_2)
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 2, core.OR: 3}
    assert stats["aliases_by_type"] == {}
    assert stats["size"] == 7
    check_behaviour()

    # merge the ands
    network.merge(and_1, and_2)
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 1, core.OR: 3}
    assert stats["aliases_by_type"] == {core.AND: 1}
    assert stats["size"] == 7
    check_behaviour()

    # merge the ors
    network.merge(or_1, or_2)
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 1, core.OR: 2}
    assert stats["aliases_by_type"] == {core.AND: 1, core.OR: 1}
    assert stats["size"] == 7
    check_behaviour()

    # try it again
    with pytest.raises(AssertionError):
        network.merge(or_1, or_2)
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 1, core.OR: 2}
    assert stats["aliases_by_type"] == {core.AND: 1, core.OR: 1}
    assert stats["size"] == 7
    check_behaviour()

    # still can't merge the third ors
    with pytest.raises(AssertionError):
        network.merge(or_3, or_2)
    stats = network.get_stats()
    assert stats["gates_by_type"] == {core.SWITCH: 2, core.AND: 1, core.OR: 2}
    assert stats["aliases_by_type"] == {core.AND: 1, core.OR: 1}
    assert stats["size"] == 7
    check_behaviour()
