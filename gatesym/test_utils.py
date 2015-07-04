from __future__ import unicode_literals, division, absolute_import

from gatesym.gates import Tie


class BinaryIn(object):
    def __init__(self, network, size, value=0):
        self.ties = [Tie(network) for i in range(size)]
        self.write(value)

    def write(self, value):
        for tie in self.ties:
            tie.write(value % 2)
            value //= 2

    def read(self):
        res = 0
        idx = 1
        for tie in self.ties:
            if tie.read():
                res += idx
            idx *= 2
        return res

    def __iter__(self):
        return iter(self.ties)

    def __len__(self):
        return len(self.ties)

    def __getitem__(self, key):
        return self.ties.__getitem__(key)


class BinaryOut(object):
    def __init__(self, gates):
        self.gates = gates

    def read(self):
        res = 0
        idx = 1
        for gate in self.gates:
            if gate.read():
                res += idx
            idx *= 2
        return res
