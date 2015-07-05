from __future__ import unicode_literals, division, absolute_import


def size(network):
    return len(network._gates)


def _longest_path(network, cache, index):
    if index not in cache:
        outputs = network._gates[index].outputs
        if len(outputs):
            cache[index] = max(_longest_path(network, cache, i) for i in outputs) + 1
        else:
            cache[index] = 1
    return cache[index]


def longest_path(network):
    cache = {}
    return max(_longest_path(network, cache, i) for i in range(len(network._gates)))
