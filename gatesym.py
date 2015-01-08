from collections import tuple


TIE, AND, OR = range(3)


class Gate(namedtuple("Gate", "type_, inputs, neg_inputs, outputs")):
    def __new__(cls, type_):
        super(Gate, cls).__new__(type_, set(), set())


class GateNetwork(object):
    def __init__(self):
        self._gates = []
        self._values = []
        self.queue = set()

    def add_gate(self, type_, inputs=[], neg_inputs=[]):
        index = len(self.gates)
        self._gates.append(Gate(type_))
        self._values.append(False)

        for input in inputs:
            self.add_link(input, index)
        for input in neg_inputs:
            self.add_link(input, index, True)

        return index

    def add_link(self, source, destination, negate=False):
        dest_gate = self._gates[destination]
        assert dest_gate.type_ != TIE
        self._gates[source].outputs.add(destination)
        if negate:
            dest_gate.neg_inputs.add(source)
        else:
            dest_gate.inputs.add(source)
        self.queue.add(destination)

    def get(self, index):
        return self.values[index]

    def set(self, index, value):
        gate = self.gates[index]
        assert gate.type_ == TIE
        self.values[index] = value
        self.queue.update(gate.outputs)

    def step(self):
        queue = self.queue
        self.queue = set()

        for index in queue:
            gate = self._gates[index]

            if gate.type_ == AND:
                i = all(self.values[i] for i in gate.inputs)
                ni = any(self.values[i] for i in gate.neg_inputs)
                res = i and not ni
            elif gate.type_ == OR:
                i = any(self.values[i] for i in gate.inputs)
                ni = all(self.values[i] for i in gate.neg_inputs)
                res = i and not ni
            else:
                assert False, gate.type_

            if self.values[index] != res:
                self.values[index] = res
                self.queue.update(gate.destination)

        return bool(self.queue)
