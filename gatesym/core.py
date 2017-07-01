""" the actual (and entire) simulation implementation """

import collections


TIE, SWITCH, AND, OR = ["tie", "switch", "and", "or"]


class _Gate(collections.namedtuple("_Gate", "type_, inputs, neg_inputs, outputs, cookies")):
    # internal gate format

    def __new__(cls, type_, cookies):
        return super().__new__(cls, type_, set(), set(), set(), cookies)


class Network(object):

    def __init__(self):
        self._gates = []
        self._values = []
        self._queue = set()
        self._watches = []
        self._log = []

    def add_gate(self, type_, cookie=None):
        assert type_ in [TIE, SWITCH, AND, OR]
        index = len(self._gates)
        self._gates.append(_Gate(type_, {cookie}))
        self._values.append(type_ == AND)
        return index

    def add_link(self, source_index, destination_index, negate=False):
        dest_gate = self._gates[destination_index]
        assert dest_gate.type_ not in {TIE, SWITCH}
        self._gates[source_index].outputs.add(destination_index)
        if negate:
            dest_gate.neg_inputs.add(source_index)
        else:
            dest_gate.inputs.add(source_index)
        self._queue.add(destination_index)

    def read(self, gate_index):
        return self._values[gate_index]

    def write(self, gate_index, value):
        if self._values[gate_index] != value:
            self._values[gate_index] = value
            self._queue.update(self._gates[gate_index].outputs)

    def step(self):
        queue = set()
        values = self._values  # localize references for speed
        gates = self._gates  # localize references for speed

        for index in self._queue:
            gate = gates[index]

            if gate.type_ == AND:
                res = all(values[i] for i in gate.inputs) and not any(values[i] for i in gate.neg_inputs)
            elif gate.type_ == OR:
                res = any(values[i] for i in gate.inputs) or not all(values[i] for i in gate.neg_inputs)
            else:
                assert False, gate.type_

            if values[index] != res:
                values[index] = res
                queue.update(gate.outputs)

        self._queue = queue
        return bool(queue)

    def drain(self):
        count = 0
        if self._queue:
            count += 1
            while self.step():
                count += 1
        return count

    def dump(self):
        for i, (v, g) in enumerate(zip(self._values, self._gates)):
            print(i, v, g)

    def record_log(self):
        new_log = []
        for name, index in self._watches:
            new_log.append(int(self.read(index)))
        self._log.append(new_log)

    def watch(self, gate_index, name):
        assert not self._log
        gate_index = self._real(gate_index)
        self._watches.append((name, gate_index))

    def print_log(self):
        if self._watches:
            name_len = max(len(n) for n, i in self._watches)
            for (name, index), row in zip(self._watches, zip(*self._log)):
                print("{0:{1}} {2}".format(name, name_len, "".join(str(i) for i in row)))
            print()

    def get_stats(self):
        gates_by_type = collections.defaultdict(int)
        gates_by_type_and_inputs = collections.defaultdict(int)
        for gate in self._gates:
            if gate:
                gates_by_type[gate.type_] += 1
                gates_by_type_and_inputs[gate.type_, len(gate.inputs) + len(gate.neg_inputs)] += 1

        return {
            "size": self.get_size(),
            "gates_by_type": gates_by_type,
            "gates_by_type_and_inputs": gates_by_type_and_inputs,
        }

    def get_size(self):
        """ total count of all gates """
        return len(self._gates)
