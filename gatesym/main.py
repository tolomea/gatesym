from gatesym.gates import Switch
from gatesym import core
from gatesym.test_utils import BinaryOut
from gatesym.computer import computer, symbols


def basic_add():
    return assemble(symbols, [], [
        123, "ADD_A",
        5, "ADD_B",
        "ADD_R", "ADD_A",
        67, "ADD_B",
        "ADD_R", "PRINT",
    ])


def loop():
    return assemble(symbols, ["i"], [
        1, "ADD_B",
        "ADD_R", "ADD_A",
        "i", "ADD_B",
        "ADD_R", "i",
        "i", "PRINT",
        0, "JUMP",
    ])


def fib():
    return assemble(symbols, [], [
        0, "ADD_A",
        1, "ADD_B",
        1, "PRINT",
        "loop:",
        "ADD_R", "PRINT",
        "ADD_R", "ADD_A",
        "ADD_R", "PRINT",
        "ADD_R", "ADD_B",
        "loop", "JUMP",
    ])


def primes():
    return assemble(symbols, ["i", "j", "tmp"], [
        3, "i",
        "start:",
        3, "j",
        "loop_start:",
        "i", "SUB_A",
        "j", "SUB_B",
        "loop_else", "JUMP_DEST",
        "SUB_R", "JUMP_ZERO",

        "i", "tmp",
        "j", "SUB_B",
        "mod_loop:",
        "tmp", "SUB_A",
        "SUB_R", "tmp",
        "loop_end", "JUMP_DEST",
        "SUB_A", "JUMP_ZERO",
        "mod_loop", "JUMP_DEST",
        "SUB_C", "JUMP_ZERO",

        2, "ADD_A",
        "j", "ADD_B",
        "ADD_R", "j",

        "loop_start", "JUMP",
        "loop_else:",
        "i", "PRINT",
        "loop_end:",
        2, "ADD_A",
        "i", "ADD_B",
        "ADD_R", "i",

        "start", "JUMP",
    ])


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
    write, res = computer(clock, primes())

    res = BinaryOut(res)
    network.drain()

    for i in range(20000):
        clock.write(True)
        network.drain()
        output = write.read()
        clock.write(False)
        network.drain()
        if output:
            print(res.read())
