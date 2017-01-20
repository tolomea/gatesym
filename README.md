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

