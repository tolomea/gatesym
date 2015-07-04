from __future__ import unicode_literals, division, absolute_import

import collections

from decorator import decorator

from gatesym import core


class Link(object):
    def __init__(self, name):
        self.name = name
        self.outputs = []

    def attach(self, output):
        self.outputs.append(output)

    def get(self, path):
        parts = path.split(".", 1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else ""
        if head:
            for l in self.outputs:
                if l.name == head:
                    return l.get(tail)
            else:
                assert False
        else:
            return self

    def list(self, path):
        return [o.name for o in self.get(path).outputs]


class Gate(Link):
    # handles to gate objects
    def __init__(self, network, index, name, inputs=[]):
        super(Gate, self).__init__(name)
        self.network = network
        self.index = index
        for input_ in inputs:
            self.add_input(input_)

    def add_input(self, input_):
        input_.attach(self)
        self.network.add_link(input_.index, self.index)

    def __repr__(self):
        return "{self.__class__.__name__}<{self.index}>({value})".format(self=self, value=self.read())

    def read(self):
        return self.network.read(self.index)


class Tie(Gate):
    def __init__(self, network, value=False):
        value = bool(value)
        index = network.add_gate(core.TIE)
        super(Tie, self).__init__(network, index, "tie")
        self.write(value)

    def write(self, value):
        self.network.write(self.index, value)


class And(Gate):
    def __init__(self, *inputs):
        network = inputs[0].network
        index = network.add_gate(core.AND)
        super(And, self).__init__(network, index, "and", inputs)


class Or(Gate):
    def __init__(self, *inputs):
        network = inputs[0].network
        index = network.add_gate(core.OR)
        super(Or, self).__init__(network, index, "or", inputs)


def nand(*inputs):
    return Not(And(*inputs))


class Proxy(Link):
    def __init__(self, gate, name):
        super(Proxy, self).__init__(name)
        self.gate = gate
        gate.attach(self)

    @property
    def network(self):
        return self.gate.network

    @property
    def index(self):
        return self.gate.index

    def read(self):
        return self.gate.read()


class Not(Proxy):
    def __init__(self, gate):
        super(Not, self).__init__(gate, "not")

    @property
    def index(self):
        return -self.gate.index

    def read(self):
        return not self.gate.read()


def proxy_factory(obj, name):
    if isinstance(obj, collections.Iterable):
        return [proxy_factory(o, name) for o in obj]
    elif isinstance(obj, Link):
        return Proxy(obj, name)
    else:
        return obj


class Block(object):
    def __init__(self, name, inputs, args, outputs):
        self.name = name
        self.inputs = inputs
        self.args = args
        if not isinstance(outputs, collections.Iterable):
            outputs = [outputs]
        self.outputs = outputs


def _block(func, *args, **kwargs):
    args = proxy_factory(args, func.__name__)
    res = func(*args, **kwargs)
    res = proxy_factory(res, func.__name__)
    Block(func.__name__, args, kwargs, res)
    return res


def block(func):
    return decorator(_block, func)
