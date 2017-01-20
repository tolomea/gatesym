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

# Core
The main class here is Network. It has the following functions of note:
* add_gate(type) - insert a new gate of the given type and return it's index, types can be AND, OR, TIE, SWITCH
* add_link(source_index, destination_index, negate) - create a link from the output of the source gate to the input of the destination, optional negated along the way
* read(gate_index) - read the output of a gate
* write(gate_index, value) - write the output of a gate, useful for ties and switches
* step() - recalculate the output of all gates currently in the queue, for any whose values change queue their outputs
* drain() - iterate on step until the queue is empty, return the number of iterations run

Internally individual gates stored in an array index by order of creation and are represented as tuples of their type, input gate indicies, negated input gate indicies and outputs gate indicies. Having negated inputs removes the need to have explicit not gates, which is useful as otherwise we'd accumulate lots of redundant not gates and I haven't figured out a convenient way of doing optimization yet.
