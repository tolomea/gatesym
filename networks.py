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


def bit_mux(address, bits):
    pass


def bit_demux(address, data):
    pass


def word_mux(address, words):
    pass


def word_demux(address, data_word):
    pass


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

""" muxes
    mux n address, 2**n inputs

    flat address
        for each input we have an And spanning all the address lines
        2**n * n

    tree address
        binary tree of pairs of 2 input Ands one tree level per address line
        except for the top level which isn't necessary
        2 * (2**(n + 1) - 4)  =  4*(2**n - 2)

    flat demux
        for each output we have an And spanning all the address lines and the input
        2**n * (n+1)

    tree demux
        binary tree of pairs of 2 input Ands one tree level per address line
        2 * (2**(n + 1) - 2)  =  4*(2**n - 1)

    flat mux
        for each input we have an And spanning all the address lines and input bit
        spanning all of the Ands is a huge Or
        ands(2**n * (n+1)) + ors(2**n)  =  2**n * (n+2)

    tree mux
        binary tree of pairs of 2 input Ands joined by ors, one tree level per addres line
        2 * (ands(2**(n+1)-2) + ors(2**n - 1))  =  6*(2**n - 1)

    to increase mux word size we can replicate the whole structure
    or have a shared address into a 2 input And per bit
    with an Or across all the bits in the same position
    for demux we can leave out the or
"""
