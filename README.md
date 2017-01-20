# Gate Simulator
* A logic gate level simulation.
* A OISC CPU implemented in said simulation
* A minimal assembler
* A couple of programs to be assembled and run on the CPU

# Files
n.b. the gates, blocks and modules functions (and constructors) all take their input gates (and any additional parameters) as arguments and return their output gate(s)
* core.py - the actual (and entire) simulation implementation
* gates.py - a convenience layer over the core that represents gates as objects making it easier to create networks of them
* utils.py - a couple of small utilities for use with the convenience layer
* test_utils.py - a couple of small utilities used in the tests
* blocks - functions for constuction several functional logic units (adders, muxes etc) from gate objects
* modules - functions for constructing cpu sub modules from gates objects and blocks
* computer.py - OISC computer, assembler and example programs

# Core.py
The main class here is Network. It represents and updates a network of gates. Gates can be of type AND, OR, TIE or SWITCH. TIE and SWITCH are both literal values that can't take inputs, there is no implementation difference between them but the symantic difference can be useful to the user.
The Network class has the following functions of note:
* add_gate(type) - insert a new gate of the given type and return it's index, types can be
* add_link(source_index, destination_index, negate) - create a link from the output of the source gate to the input of the destination, optional negated along the way
* read(gate_index) - read the output of a gate
* write(gate_index, value) - write the output of a gate, useful for ties and switches
* step() - recalculate the output of all gates currently in the queue, for any whose values change queue their outputs
* drain() - iterate on step until the queue is empty, return the number of iterations run
There is also some minimal debugging support
* watch(gate_index, name) - flag the given gate to be included in logging
* record_log() - log the current values of the flagged gates
* print_log() - dump out the log contents

Internally individual gates are stored in an array indexed by order of creation and are represented as tuples of their type, input gate indicies, negated input gate indicies and outputs gate indicies. Having negated inputs removes the need to have explicit not gates, which is useful as otherwise we'd accumulate lots of redundant not gates and I haven't figured out a convenient way of doing optimization yet.

# Gates.py
While the core makes for a reasonably fast simulation it's not the most user friendly. Gates builds a logical layer over the physical layer of of the core. This layer makes construction and debugging of gate networks far more convenient. In this layer Gates are represented as objects which know their underlying network and index. There is also a higher level Node abstraction from which Gates inherit, this lets us have virtual gates for points in the network that don't have actual gates. Classes of note are:
* Node - a point in the Gate graph
* Gate - a Node which is associated with a gate in the underlying core Network
* Tie / Switch / And / Or - the various gate types from the core
* Not - a virtual Gate that serves as a convenience access for another Gate with it's output negated
* Link - a marker for an interesting point in the network, convenient for marking module boundaries
* Placeholder - a virtual gate to hold a place until the actual gate is provided later, unseful for constructing loops
* Block - represents a functional block, intended to be used with the block decorator
* block - treats the arguments and return of a function as a block boundary creating useful Link nodes

Nodes have names and some useful debugging functionality for traversing the network by name including:
* find(path) - starting at the given node traverse the path given and return the node found there
* list(path) - list all possible next steps from the node returned by find(path)
* full_name() - follow the first input back recursively to until you reach a node with no inputs and print the path from there to here

When traversing nodes like this you can skip from a block input directly to any output of the same block


