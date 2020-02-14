from gatesym.gates import Switch
from gatesym import core
from gatesym.test_utils import BinaryOut
from gatesym.computer import computer, symbols
import string


def basic_add():
    return assemble(
        symbols,
        [],
        [123, "ADD_A", 5, "ADD_B", "ADD_R", "ADD_A", 67, "ADD_B", "ADD_R", "PRINT"],
    )


def loop():
    return assemble(
        symbols,
        ["i"],
        [
            1,
            "ADD_B",
            "ADD_R",
            "ADD_A",
            "i",
            "ADD_B",
            "ADD_R",
            "i",
            "i",
            "PRINT",
            0,
            "JUMP",
        ],
    )


def fib():
    return assemble(
        symbols,
        [],
        [
            0,
            "ADD_A",
            1,
            "ADD_B",
            1,
            "PRINT",
            "loop:",
            "ADD_R",
            "PRINT",
            "ADD_R",
            "ADD_A",
            "ADD_R",
            "PRINT",
            "ADD_R",
            "ADD_B",
            "loop",
            "JUMP",
        ],
    )


def primes():
    return assemble(
        symbols,
        ["i"],
        [
            # j is in ADD_B
            2,
            "ADD_A",
            # i = 3
            # start:
            # j = 3
            # loop_start:
            # if i - j == 0: goto loop_else  # ran out of numbers to check so i is prime
            3,
            "i",
            "start:",
            3,
            "ADD_B",
            "loop_start:",
            "i",
            "SUB_A",
            "ADD_B",
            "SUB_B",
            "loop_else",
            "JUMP_DEST",
            "SUB_R",
            "JUMP_IF_ZERO",
            # tmp is in SUB_A
            # tmp = i
            # # while tmp > 0: tmp -= j
            # mod_loop:
            # if tmp - j < 0: goto mod_end
            # tmp -= j
            # goto mod_loop
            # mod_end:
            "i",
            "SUB_A",
            "ADD_B",
            "SUB_B",
            "mod_end",
            "JUMP_DEST",
            "mod_loop:",
            "SUB_C",
            "JUMP_IF_NON_ZERO",
            "SUB_R",
            "SUB_A",
            "mod_loop",
            "JUMP",
            "mod_end:",
            # if tmp == 0: goto loop_end  # divides equally, not prime
            "loop_end",
            "JUMP_DEST",
            "SUB_A",
            "JUMP_IF_ZERO",
            # j += 2
            "ADD_R",
            "ADD_B",
            # goto loop_start
            "loop_start",
            "JUMP",
            # loop_else:
            # print i
            "loop_else:",
            "i",
            "PRINT",
            # loop_end:
            # i += 2
            "loop_end:",
            "i",
            "ADD_B",
            "ADD_R",
            "i",
            # goto start
            "start",
            "JUMP",
        ],
    )


def hello_world():
    program = []
    for c in "Hello World !":
        program.extend([ord(c), "PRINT"])
    program.extend([1, "HALT"])
    return assemble(symbols, [], program)


def assemble(symbols, variables, code):
    symbols = dict(symbols)
    for offset, name in enumerate(variables):
        symbols[name] = symbols["_RAM"] + offset

    # collect jump labels
    i = 0
    for c in code:
        if isinstance(c, str) and c.endswith(":"):
            symbols[c[:-1]] = symbols["_LIT"] + i
        else:
            i += 1

    # convert symbols and int's to addresses
    res = []
    for c in code:
        if isinstance(c, str):
            if not c.endswith(":"):
                res.append(symbols[c])
        else:
            res.append(symbols["_LIT"] + c)
    return res


def main():
    network = core.Network()
    clock = Switch(network)
    write, res, halt = computer(clock, hello_world())
    print()

    res = BinaryOut(res)
    network.drain()

    print("cycles int   hex  char")
    last = 0
    for i in range(5000):
        clock.write(True)
        network.drain()
        output = write.read()
        clock.write(False)
        network.drain()
        if output:
            val = res.read()
            try:
                c = chr(val)
            except:
                c = "\u2610"
            if c not in string.ascii_letters + string.digits + string.punctuation + " ":
                c = "\u2610"
            print(f"{i - last:6} {val:5} {val:04x} {c}")
            last = i
        if halt.read():
            print("explicit halt")
            break
