from __future__ import unicode_literals, division, absolute_import

import collections


TIE, AND, OR = range(3)


class _Gate(collections.namedtuple("_Gate", "type_, inputs, neg_inputs, outputs")):
    # internal gate format
    def __new__(cls, type_):
        return super(_Gate, cls).__new__(cls, type_, set(), set(), set())


class Network(object):
    def __init__(self):
        self._gates = [None]
        self._values = [None]
        self._queue = set()

    def add_gate(self, type_):
        assert type_ in [TIE, AND, OR]
        index = len(self._gates)
        self._gates.append(_Gate(type_))
        self._values.append(False)
        return index

    def add_link(self, source, destination):
        assert source.network is self
        assert destination.network is self
        assert destination.index > 0
        dest_gate = self._gates[destination.index]
        assert dest_gate.type_ != TIE
        self._gates[abs(source.index)].outputs.add(destination.index)
        if source.index < 0:
            dest_gate.neg_inputs.add(abs(source.index))
        else:
            dest_gate.inputs.add(source.index)
        self._queue.add(destination.index)

    def read(self, gate):
        assert gate.network is self
        if gate.index < 0:
            return not self._values[-gate.index]
        else:
            return self._values[gate.index]

    def write(self, gate, value):
        assert gate.network is self
        assert gate.index > 0
        r_gate = self._gates[gate.index]
        assert r_gate.type_ == TIE
        self._values[gate.index] = value
        self._queue.update(r_gate.outputs)

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
        count = 1
        while self.step():
            count += 1
        return count
