from __future__ import unicode_literals, division, absolute_import

""" the actual (and entire) simulation implementation """

import collections


TIE, SWITCH, AND, OR = range(4)


class _Gate(collections.namedtuple("_Gate", "type_, inputs, neg_inputs, outputs, cookie")):
    # internal gate format

    def __new__(cls, type_, cookie):
        return super(_Gate, cls).__new__(cls, type_, set(), set(), set(), cookie)


class Network(object):

    def __init__(self):
        self._gates = []
        self._values = []
        self._queue = set()
        self.watches = []
        self.log = []

    def add_gate(self, type_, cookie):
        assert type_ in [TIE, SWITCH, AND, OR]
        index = len(self._gates)
        self._gates.append(_Gate(type_, cookie))
        self._values.append(False)
        return index

    def add_link(self, source_index, destination_index, negate=False):
        assert destination_index >= 0
        assert source_index >= 0
        dest_gate = self._gates[destination_index]
        assert dest_gate.type_ not in {TIE, SWITCH}
        self._gates[source_index].outputs.add(destination_index)
        if negate:
            dest_gate.neg_inputs.add(source_index)
        else:
            dest_gate.inputs.add(source_index)
        self._queue.add(destination_index)

    def read(self, gate_index):
        assert gate_index >= 0
        return self._values[gate_index]

    def write(self, gate_index, value):
        assert gate_index >= 0
        r_gate = self._gates[gate_index]
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
            print(i, v, g)

    def record_log(self):
        new_log = []
        for name, index in self.watches:
            new_log.append(int(self.read(index)))
        self.log.append(new_log)

    def watch(self, index, name):
        assert not self.log
        self.watches.append((name, index))

    def print_log(self):
        if self.watches:
            name_len = max(len(n) for n, i in self.watches)
            for (name, index), row in zip(self.watches, zip(*self.log)):
                print("{0:{1}} {2}".format(name, name_len, "".join(str(i) for i in row)))
            print()
