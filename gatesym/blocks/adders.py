from gatesym.gates import And, Or, Not, block, Tie


@block
def half_adder(a, b):
    """ add two bits, return a sum and a carry """
    carry = And(a, b)
    result = Or(And(a, Not(b)), And(Not(a), b))
    return result, carry


@block
def full_adder(a, b, c):
    """ chain two half adders to add two bits and a previous carry, again returning a sum and a carry """
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, c)
    return s2, Or(c1, c2)


@block
def ripple_adder(aw, bw):
    """ chain multiple full_adders to add two words returning a sum word and a carry bit """
    assert len(aw) == len(bw)
    r, c = half_adder(aw[0], bw[0])
    rw = [r]
    for a, b in zip(aw[1:], bw[1:]):
        r, c = full_adder(a, b, c)
        rw.append(r)
    return rw, c


@block
def ripple_incr(word):
    """ increment a word by 1 """
    c = Tie(word[0].network, True)
    rw = []
    for a in word:
        r, c = half_adder(a, c)
        rw.append(r)
    return rw, c


@block
def ripple_sum(*words):
    """ sum multiple words """
    carries = []
    # iterate building layers of a binary tree structure
    while len(words) > 1:
        new_words = []
        # add every adjacent pair, so 1+2, 3+4 etc
        for a, b in zip(words[::2], words[1::2]):
            res, carry = ripple_adder(a, b)
            carries.append(carry)
            new_words.append(res)
        # if there is one left at the end just keep it in the next level up
        if len(words) % 2:
            new_words.append(words[-1])
        words = new_words
    return words[0], Or(*carries)


@block
def half_subtractor(a, b):
    """ subtract bit B from bit A, return a difference and a borrow """
    borrow = And(Not(a), b)
    result = Or(And(a, Not(b)), And(Not(a), b))
    return result, borrow


@block
def full_subtractor(a, b, c):
    """
    chain two half subtractors to subtract bit B and previous borrow from A, again returning a difference and a borrow
    """
    s1, c1 = half_subtractor(a, b)
    s2, c2 = half_subtractor(s1, c)
    return s2, Or(c1, c2)


@block
def ripple_subtractor(aw, bw):
    """ chain multiple full_subtractors to subtract word B from word A returning a difference word and a borrow bit """
    assert len(aw) == len(bw)
    r, c = half_subtractor(aw[0], bw[0])
    rw = [r]
    for a, b in zip(aw[1:], bw[1:]):
        r, c = full_subtractor(a, b, c)
        rw.append(r)
    return rw, c
