import collections

from gatesym.gates import Switch


class BinaryIn(collections.Sequence):
    def __init__(self, network, size, value=0):
        self.switches = [Switch(network) for i in range(size)]
        self.write(value)

    def write(self, value):
        for switch in self.switches:
            switch.write(value % 2)
            value //= 2

    def read(self):
        res = 0
        idx = 1
        for switch in self.switches:
            if switch.read():
                res += idx
            idx *= 2
        return res

    def __iter__(self):
        return iter(self.switches)

    def __len__(self):
        return len(self.switches)

    def __getitem__(self, key):
        return self.switches.__getitem__(key)


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
