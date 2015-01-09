from collections import namedtuple


TIE, AND, OR = range(3)


class Gate(namedtuple("Gate", "type_, inputs, neg_inputs, outputs")):
    def __new__(cls, type_):
        return super(Gate, cls).__new__(cls, type_, set(), set(), set())


class GateNetwork(object):
    def __init__(self):
        self._gates = [None]
        self._values = [None]
        self._queue = set()

    def add_gate(self, type_, *inputs):
        index = len(self._gates)
        self._gates.append(Gate(type_))
        self._values.append(False)

        for input_ in inputs:
            self.add_link(input_, index)

        return index

    def add_link(self, source, destination):
        dest_gate = self._gates[destination]
        assert dest_gate.type_ != TIE
        self._gates[abs(source)].outputs.add(destination)
        if source < 0:
            dest_gate.neg_inputs.add(abs(source))
        else:
            dest_gate.inputs.add(source)
        self._queue.add(destination)

    def get(self, index):
        return self._values[index]

    def set(self, index, value):
        gate = self._gates[index]
        assert gate.type_ == TIE
        self._values[index] = value
        self._queue.update(gate.outputs)

    def step(self):
        queue = self._queue
        self._queue = set()

        for index in queue:
            gate = self._gates[index]

            if gate.type_ == AND:
                a = [self._values[i] for i in gate.inputs]
                b = [not self._values[i] for i in gate.neg_inputs]
                res = all(a + b)
            elif gate.type_ == OR:
                a = [self._values[i] for i in gate.inputs]
                b = [not self._values[i] for i in gate.neg_inputs]
                res = any(a + b)
            else:
                assert False, gate.type_

            if self._values[index] != res:
                self._values[index] = res
                self._queue.update(gate.outputs)

        return bool(self._queue)

    def drain(self):
        print ".",
        while self.step():
            print ".",
            pass
        print


def Not(input_):
    return -input_


def half_adder(network, a, b):
    carry = network.add_gate(AND, a, b)
    result = network.add_gate(
        OR,
        network.add_gate(AND, a, Not(b)),
        network.add_gate(AND, Not(a), b),
    )
    return result, carry


def full_adder(network, a, b, c):
    s1, c1 = half_adder(network, a, b)
    s2, c2 = half_adder(network, s1, c)
    return s2, network.add_gate(OR, c1, c2)


def test_half_adder():
    network = GateNetwork()
    a = network.add_gate(TIE)
    b = network.add_gate(TIE)
    r, c = half_adder(network, a, b)
    network.drain()

    network.set(a, False)
    network.set(b, False)
    network.drain()
    assert not network.get(r)
    assert not network.get(c)

    network.set(a, True)
    network.set(b, False)
    network.drain()
    assert network.get(r)
    assert not network.get(c)

    network.set(a, False)
    network.set(b, True)
    network.drain()
    assert network.get(r)
    assert not network.get(c)

    network.set(a, True)
    network.set(b, True)
    network.drain()
    assert not network.get(r)
    assert network.get(c)


def test_full_adder():
    network = GateNetwork()
    a = network.add_gate(TIE)
    b = network.add_gate(TIE)
    c = network.add_gate(TIE)
    r, co = full_adder(network, a, b, c)
    network.drain()

    network.set(a, False)
    network.set(b, False)
    network.set(c, False)
    network.drain()
    assert not network.get(r)
    assert not network.get(co)

    network.set(a, True)
    network.set(b, False)
    network.set(c, False)
    network.drain()
    assert network.get(r)
    assert not network.get(co)

    network.set(a, False)
    network.set(b, True)
    network.set(c, False)
    network.drain()
    assert network.get(r)
    assert not network.get(co)

    network.set(a, True)
    network.set(b, True)
    network.set(c, False)
    network.drain()
    assert not network.get(r)
    assert network.get(co)

    network.set(a, False)
    network.set(b, False)
    network.set(c, True)
    network.drain()
    assert network.get(r)
    assert not network.get(co)

    network.set(a, True)
    network.set(b, False)
    network.set(c, True)
    network.drain()
    assert not network.get(r)
    assert network.get(co)

    network.set(a, False)
    network.set(b, True)
    network.set(c, True)
    network.drain()
    assert not network.get(r)
    assert network.get(co)

    network.set(a, True)
    network.set(b, True)
    network.set(c, True)
    network.drain()
    assert network.get(r)
    assert network.get(co)


if __name__ == "__main__":
    test_half_adder()
    test_full_adder()
