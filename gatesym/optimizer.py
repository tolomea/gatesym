from gatesym import core


def flatten_ties(network):
    true_tie_idx = None
    false_tie_idx = None
    for idx, gate in network.all_gates():
        if gate.type_ == core.TIE:
            if network.read(idx):
                if true_tie_idx is None:
                    true_tie_idx = idx
                else:
                    network.merge(idx, true_tie_idx)
            else:
                if false_tie_idx is None:
                    false_tie_idx = idx
                else:
                    network.merge(idx, false_tie_idx)


def _get_peer_indicies(network, idx):
    for output_idx in network.get_gate(idx).outputs:
        output = network.get_gate(output_idx)
        if output:
            yield from set(output.inputs)
            yield from set(output.neg_inputs)


def remove_duplicates(network):
    queue = set(k for k, v in network.all_gates())
    while(queue):
        idx = queue.pop()
        gate = network.get_gate(idx)
        if gate:  # it may have been merged already
            for peer_idx in _get_peer_indicies(network, idx):
                network
                if network.can_merge(peer_idx, idx):
                    print("merging", peer_idx, idx)
                    network.merge(peer_idx, idx)


def optimize(network):
    flatten_ties(network)
    remove_duplicates(network)


"""
gates with no inputs
gates with no outputs
1 input gates
"""
