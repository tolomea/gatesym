from __future__ import unicode_literals, division, absolute_import

from gatesym import gates


def size(network):
    return len(network._gates)


def _longest_gate_path(network, cache, index):
    if index not in cache:
        outputs = network._gates[index].outputs
        if len(outputs):
            cache[index] = max(_longest_gate_path(network, cache, i) for i in outputs) + 1
        else:
            cache[index] = 1
    return cache[index]


def longest_gate_path(network):
    cache = {}
    return max(_longest_gate_path(network, cache, i) for i in range(len(network._gates)))


def _longest_node_path(cache, node):
    if node not in cache:
        outputs = node.outputs
        if len(outputs):
            longest_len = -1
            longest_name = ""
            for o in outputs:
                l, n = _longest_node_path(cache, o)
                if l > longest_len:
                    longest_len = l
                    longest_name = n
            name = node.name
            if longest_name:
                name += "." + longest_name
            cache[node] = longest_len, name
        else:
            cache[node] = 0, node.name
        if isinstance(node, gates.Gate):
            l, n = cache[node]
            cache[node] = l + 1, n
    return cache[node]


def longest_node_path(starts):
    cache = {}
    return max(_longest_node_path(cache, node) for node in starts)
