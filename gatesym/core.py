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

    def add_link(self, source_index, destination_index):
        assert destination_index > 0
        dest_gate = self._gates[destination_index]
        assert dest_gate.type_ != TIE
        self._gates[abs(source_index)].outputs.add(destination_index)
        if source_index < 0:
            dest_gate.neg_inputs.add(abs(source_index))
        else:
            dest_gate.inputs.add(source_index)
        self._queue.add(destination_index)

    def read(self, gate_index):
        assert gate_index > 0
        return self._values[gate_index]

    def write(self, gate_index, value):
        assert gate_index > 0
        r_gate = self._gates[gate_index]
        assert r_gate.type_ == TIE
        self._values[gate_index] = value
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

    def dump(self):
        for i, (v, g) in enumerate(zip(self._values, self._gates)):
            print i, v, g
