from gatesym import Network, And, Or, Not, Tie, BinaryIn, BinaryOut
import random


def half_adder(a, b):
    carry = And(a, b)
    result = Or(And(a, Not(b)), And(Not(a), b))
    return result, carry


def full_adder(a, b, c):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, c)
    return s2, Or(c1, c2)


def ripple_adder(aw, bw):
    assert len(aw) == len(bw)
    r, c = half_adder(aw[0], bw[0])
    rw = [r]
    for a, b in zip(aw, bw)[1:]:
        r, c = full_adder(a, b, c)
        rw.append(r)
    return rw, c


def test_half_adder():
    network = Network()
    a = Tie(network)
    b = Tie(network)
    r, c = half_adder(a, b)
    network.drain()

    a.write(False)
    b.write(False)
    network.drain()
    assert not r.read()
    assert not c.read()

    a.write(True)
    b.write(False)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(False)
    b.write(True)
    network.drain()
    assert r.read()
    assert not c.read()

    a.write(True)
    b.write(True)
    network.drain()
    assert not r.read()
    assert c.read()


def test_full_adder():
    network = Network()
    a = Tie(network)
    b = Tie(network)
    c = Tie(network)
    r, co = full_adder(a, b, c)
    network.drain()

    a.write(False)
    b.write(False)
    c.write(False)
    network.drain()
    assert not r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(False)
    b.write(True)
    c.write(False)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(True)
    c.write(False)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(False)
    c.write(True)
    network.drain()
    assert r.read()
    assert not co.read()

    a.write(True)
    b.write(False)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(False)
    b.write(True)
    c.write(True)
    network.drain()
    assert not r.read()
    assert co.read()

    a.write(True)
    b.write(True)
    c.write(True)
    network.drain()
    assert r.read()
    assert co.read()


def test_ripple_adder():
    network = Network()
    a = BinaryIn(network, 8)
    b = BinaryIn(network, 8)
    r, c = ripple_adder(a, b)
    r = BinaryOut(r)

    for i in range(10):
        v1 = random.randrange(256)
        v2 = random.randrange(256)
        print v1, v2
        a.write(v1)
        b.write(v2)
        network.drain()
        assert c.read() == (v1 + v2 >= 256)
        assert r.read() == (v1 + v2) % 256


if __name__ == "__main__":
    test_half_adder()
    test_full_adder()
    test_ripple_adder()
