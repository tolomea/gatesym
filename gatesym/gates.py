from __future__ import unicode_literals, division, absolute_import

""" a convenience layer for creating data in the core and debugging it """

import collections

from decorator import decorator

from gatesym import core


class Node(object):
    """ a point in the network of gates """
    def __init__(self, name, block=None):
        self.name = name
        self.outputs = []
        self.block = block

    def attach_output(self, output):
        self.outputs.append(output)

    @property
    def all_outputs(self):
        if self.block:
            return self.block.outputs + self.outputs
        else:
            return self.outputs

    def find(self, path, location=""):
        if location:
            location = location + "."
        location = location + self.name
        parts = path.split(".", 1)
        head = parts[0]
        tail = parts[1] if len(parts) > 1 else ""
        if head:
            for l in self.all_outputs:
                if l.name == head:
                    return l.find(tail, location)
            else:
                raise ValueError("at " + location + " expected one of " + repr([o.name for o in self.outputs]))
        else:
            return self

    def list(self, path):
        return [o.name for o in self.find(path).all_outputs]

    def watch(self, name):
        self.network.watch(self.index, name)


class Gate(Node):
    """ handles to gates in the core """
    def __init__(self, network, index, name, inputs=[]):
        super(Gate, self).__init__(name)
        self.network = network
        self.index = index
        for input_ in inputs:
            self.add_input(input_)

    def add_input(self, input_):
        input_.attach_output(self)
        input_.connect_output(self, False)

    def __repr__(self):
        return "{self.__class__.__name__}<{self.index}>({value})".format(self=self, value=self.read())

    def read(self):
        return self.network.read(self.index)

    def connect_output(self, output, negate):
        self.network.add_link(self.index, output.index, negate)


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
        assert inputs
        network = inputs[0].network
        index = network.add_gate(core.AND)
        super(And, self).__init__(network, index, "and", inputs)


class Or(Gate):
    def __init__(self, *inputs):
        assert inputs
        network = inputs[0].network
        index = network.add_gate(core.OR)
        super(Or, self).__init__(network, index, "or", inputs)


def nand(*inputs):
    return Not(And(*inputs))


class Link(Node):
    """ interesting steps along the path between two gates """
    def __init__(self, node, name, block=None):
        super(Link, self).__init__(name, block=block)
        self.node = node
        node.attach_output(self)

    @property
    def network(self):
        return self.node.network

    def read(self):
        return self.node.read()

    def connect_output(self, output, negate):
        return self.node.connect_output(output, negate)

    @property
    def index(self):
        return self.node.index


class Not(Link):
    def __init__(self, node):
        super(Not, self).__init__(node, "not")

    def read(self):
        return not self.node.read()

    def connect_output(self, output, negate):
        return self.node.connect_output(output, not negate)


class Placeholder(Node):
    """ a placeholder we will replace with a real node later """
    def __init__(self, network):
        super(Placeholder, self).__init__("placeholder")
        self.network = network
        self.connected = []
        self.actual = None

    def connect_output(self, output, negate):
        if self.actual:
            self.actual.connect_output(output, negate)
        else:
            self.connected.append((output, negate))

    def replace(self, input):
        self.actual = input
        for o in self.outputs:
            input.attach_output(o)
        for o, n in self.connected:
            input.connect_output(o, n)

    def __getattr__(self, name):
        assert self.actual
        return getattr(self.actual, name)


def link_factory(obj, name1, name2, in_block=None, out_block=None):
    """ wrap links around a bunch of nodes in an arbitrarily nested structure """
    if isinstance(obj, collections.Iterable):
        if name1 and not name1.endswith("("):
            name1 = name1 + ","
        return [link_factory(o, name1 + str(i), name2, in_block, out_block) for i, o in enumerate(obj)]
    elif isinstance(obj, Node):
        l = Link(obj, name1 + name2, block=in_block)
        if out_block:
            out_block.outputs.append(l)
        return l
    else:
        return obj


class Block(object):
    """ wrapper around a functional block """
    def __init__(self, name):
        self.name = name
        self.outputs = []


def _block(func, *args):
    block = Block(func.__name__)
    args = link_factory(args, func.__name__ + "(", "", in_block=block)
    res = func(*args)
    res = link_factory(res, "", ")", out_block=block)
    return res


def block(func):
    return decorator(_block, func)
