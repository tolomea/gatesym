""" a convenience layer for creating data in the core and debugging it """

import collections

from decorator import decorator

from gatesym import core


class Node(object):
    """ a point in the network of gates """

    def __init__(self, name):
        self.name = name
        self.outputs = []
        self.inputs = []
        self.block = None

    def attach_output(self, output):
        """ connect an output at the logical level, output can be any node """
        self.outputs.append(output)
        output.inputs.append(self)

    def connect_output(self, output, negate):
        """ connect an output at the phycical level, output must be a gate """
        raise NotImplementedError

    @property
    def all_outputs(self):
        return self.outputs

    def find(self, path, location=""):
        """ look up a related node by path """
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
                raise ValueError(
                    "at "
                    + location
                    + " expected one of "
                    + repr([o.name for o in self.outputs])
                )
        else:
            return self

    def list(self, path):
        """ look up a related node by path and list it's outputs """
        return [o.name for o in self.find(path).all_outputs]

    def watch(self, name):
        """ set a watch on this node """
        self.network.watch(self.index, name, False)

    def full_name(self):
        """
        trace the first inputs back until we find a node with no inputs and return the path from there to here
        this could be better, jumping across blocks for example
        """
        possible_inputs = [i for i in self.inputs if ")" not in i.name]

        if possible_inputs:
            print([i.name for i in self.inputs])
            return possible_inputs[0].full_name() + "." + self.name
        else:
            print([i.name for i in self.inputs])
            return self.name


class Gate(Node):
    """ handles to gates in the core """

    def __init__(self, network, index, name, inputs=[]):
        super().__init__(name)
        self.network = network
        self.index = index
        for input_ in inputs:
            input_.attach_output(self)
            input_.connect_output(self, False)

    def __repr__(self):
        return "{self.__class__.__name__}<{self.index}>({value})".format(
            self=self, value=self.read()
        )

    def read(self):
        return self.network.read(self.index)

    def connect_output(self, output, negate):
        self.network.add_link(self.index, output.index, negate)


class Tie(Gate):
    def __init__(self, network, value):
        value = bool(value)
        index = network.add_gate(core.TIE, self)
        super().__init__(network, index, "tie")
        self.network.write(self.index, value)


class Switch(Gate):
    def __init__(self, network, value=False):
        value = bool(value)
        index = network.add_gate(core.SWITCH, self)
        super().__init__(network, index, "switch")
        self.write(value)

    def write(self, value):
        self.network.write(self.index, value)


class And(Gate):
    def __init__(self, *inputs):
        assert inputs
        network = inputs[0].network
        index = network.add_gate(core.AND, self)
        super().__init__(network, index, "and", inputs)


class Or(Gate):
    def __init__(self, *inputs):
        assert inputs
        network = inputs[0].network
        index = network.add_gate(core.OR, self)
        super().__init__(network, index, "or", inputs)


def nand(*inputs):
    return Not(And(*inputs))


class Link(Node):
    """ interesting steps along the path between two gates """

    def __init__(self, node, name, block, is_output):
        super().__init__(name)
        self.block = block
        self.is_output = is_output
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

    @property
    def all_outputs(self):
        if self.block and not self.is_output:
            return self.block.outputs + self.outputs
        else:
            return self.outputs


class Not(Link):
    def __init__(self, node):
        super().__init__(node, "not", None, False)

    def read(self):
        return not self.node.read()

    def connect_output(self, output, negate):
        return self.node.connect_output(output, not negate)

    def watch(self, name):
        """ set a watch on this node """
        self.network.watch(self.index, name, True)


class Placeholder(Node):
    """ a placeholder we will replace with a real node later """

    def __init__(self, network):
        super().__init__("placeholder")
        self.network = network
        self.connected = []
        self.attached = []
        self.actual = None

    def attach_output(self, output):
        """ connect an output at the logical level, output can be any node """
        if self.actual:
            self.actual.attach_output(output)
        else:
            self.attached.append(output)

    def connect_output(self, output, negate):
        if self.actual:
            self.actual.connect_output(output, negate)
        else:
            self.connected.append((output, negate))

    def replace(self, input):
        assert not self.actual
        self.actual = input
        for o in self.attached:
            input.attach_output(o)
        for o, n in self.connected:
            input.connect_output(o, n)

    def __getattr__(self, name):
        assert self.actual
        return getattr(self.actual, name)


def link_factory(obj, name1, name2, block, is_output):
    """ wrap links around a bunch of nodes in an arbitrarily nested structure """
    if isinstance(obj, collections.Iterable):
        if name1 and not name1.endswith("("):
            name1 = name1 + ","
        return [
            link_factory(o, name1 + str(i), name2, block, is_output)
            for i, o in enumerate(obj)
        ]
    elif isinstance(obj, Node):
        link = Link(obj, name1 + name2, block, is_output)
        if is_output:
            block.outputs.append(link)
        else:
            block.inputs.append(link)
        return link
    else:
        return obj


class Block(object):
    """ wrapper around a functional block, intended to be used via the decorator below """

    def __init__(self, name):
        self.name = name
        self.outputs = []
        self.inputs = []
        self.size = None


def _find_network(thing):
    """
    given a bunch of nested stuff find one that has a network property and return it
    the existance of this speaks to issues with how I'm handling the relations between blocks and nodes and the network
    """
    if hasattr(thing, "network"):
        return thing.network
    if isinstance(thing, collections.Iterable):
        for item in thing:
            tmp = _find_network(item)
            if tmp:
                return tmp
    return None


def _block(func, *args):
    network = _find_network(args)
    old_size = network.get_size()

    block = Block(func.__name__)

    args = link_factory(args, func.__name__ + "(", "", block, False)
    res = func(*args)
    res = link_factory(res, "", ")", block, True)

    block.size = network.get_size() - old_size

    return res


def block(func):
    return decorator(_block, func)
