from gatesym import core, gates, test_utils
from gatesym.modules import jump


def test_jump():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 2)
    data_in = test_utils.BinaryIn(network, 8)
    jump_out, pc_in, pc_write = jump.jump(clock, write_flag, address, data_in)
    jump_out = test_utils.BinaryOut(jump_out)
    pc_in = test_utils.BinaryOut(pc_in)
    network.drain()

    data_in.write(123)
    address.write(0)
    network.drain()
    assert not pc_write.read()

    write_flag.write(True)
    network.drain()
    assert pc_in.read() == 123
    assert pc_write.read()

    write_flag.write(False)
    network.drain()
    assert not pc_write.read()


def test_jump_zero_with_zero():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 2)
    data_in = test_utils.BinaryIn(network, 8)
    jump_out, pc_in, pc_write = jump.jump(clock, write_flag, address, data_in)
    jump_out = test_utils.BinaryOut(jump_out)
    pc_in = test_utils.BinaryOut(pc_in)
    network.drain()

    data_in.write(212)
    address.write(1)
    write_flag.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(0)
    network.drain()
    assert not pc_write.read()
    write_flag.write(0)

    data_in.write(0)
    address.write(2)
    network.drain()
    assert not pc_write.read()

    write_flag.write(1)
    network.drain()
    assert pc_write.read()
    assert pc_in.read() == 212


def test_no_jump_zero_with_non_zero():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 2)
    data_in = test_utils.BinaryIn(network, 8)
    jump_out, pc_in, pc_write = jump.jump(clock, write_flag, address, data_in)
    jump_out = test_utils.BinaryOut(jump_out)
    pc_in = test_utils.BinaryOut(pc_in)
    network.drain()

    data_in.write(212)
    address.write(1)
    write_flag.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(0)
    network.drain()
    assert not pc_write.read()
    write_flag.write(0)

    data_in.write(1)
    address.write(2)
    network.drain()
    assert not pc_write.read()

    write_flag.write(1)
    network.drain()
    assert not pc_write.read()


def test_jump_non_zero_with_zero():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 2)
    data_in = test_utils.BinaryIn(network, 8)
    jump_out, pc_in, pc_write = jump.jump(clock, write_flag, address, data_in)
    jump_out = test_utils.BinaryOut(jump_out)
    pc_in = test_utils.BinaryOut(pc_in)
    network.drain()

    data_in.write(212)
    address.write(1)
    write_flag.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(0)
    network.drain()
    assert not pc_write.read()
    write_flag.write(0)

    data_in.write(0)
    address.write(3)
    network.drain()
    assert not pc_write.read()

    write_flag.write(1)
    network.drain()
    assert not pc_write.read()


def test_no_jump_non_zero_with_non_zero():
    network = core.Network()
    clock = gates.Switch(network)
    write_flag = gates.Switch(network)
    address = test_utils.BinaryIn(network, 2)
    data_in = test_utils.BinaryIn(network, 8)
    jump_out, pc_in, pc_write = jump.jump(clock, write_flag, address, data_in)
    jump_out = test_utils.BinaryOut(jump_out)
    pc_in = test_utils.BinaryOut(pc_in)
    network.drain()

    data_in.write(212)
    address.write(1)
    write_flag.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(1)
    network.drain()
    assert not pc_write.read()

    clock.write(0)
    network.drain()
    assert not pc_write.read()
    write_flag.write(0)

    data_in.write(1)
    address.write(3)
    network.drain()
    assert not pc_write.read()

    write_flag.write(1)
    network.drain()
    assert pc_write.read()
    assert pc_in.read() == 212
