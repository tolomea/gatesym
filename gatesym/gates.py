from __future__ import unicode_literals, division, absolute_import

import functools
import collections

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
            input_.attach(self)
            network.add_link(input_, self)

    def __repr__(self):
        return "{self.index}".format(self=self)

    def read(self):
        return self.network.read(self)


class Tie(Gate):
    def __init__(self, network, value=False):
        index = network.add_gate(core.TIE)
        super(Tie, self).__init__(network, index, "tie")
        self.write(value)

    def write(self, value):
        self.network.write(self, value)


def Not(gate):
    res = Gate(gate.network, -gate.index, "not")
    gate.attach(res)
    return res


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


def proxy_factory(obj, name):
    if isinstance(obj, collections.Iterable):
        return [Proxy(o, name) for o in obj]
    else:
        return Proxy(obj, name)


class Block(object):
    def __init__(self, name, inputs, args, outputs):
        self.name = name
        self.inputs = inputs
        self.args = args
        self.outputs = outputs

    def __iter__(self):
        return iter(self.outputs)


def block():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args = [proxy_factory(arg, func.__name__) for arg in args]
            res = func(*args, **kwargs)
            res = [proxy_factory(r, func.__name__) for r in res]
            return Block(func.__name__, args, kwargs, res)
        return wrapper
    return decorator
