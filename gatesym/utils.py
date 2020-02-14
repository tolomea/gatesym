import collections

from gatesym.gates import Tie, Placeholder, Or


def pad(word, length, value=False):
    """ right pad a word out to a specific length """
    tie = Tie(word[0].network, value)
    return word + [tie] * (length - len(word))


def tie_word(network, size, value=0):
    """ an entire word of ties """
    res = []
    for i in range(size):
        res.append(Tie(network, value=value % 2))
        value //= 2
    return res


class PlaceholderWord(collections.Sequence):
    """ an entire word of placeholders """

    def __init__(self, network, size):
        self.placeholders = [Placeholder(network) for i in range(size)]

    def __len__(self):
        return len(self.placeholders)

    def __getitem__(self, index):
        return self.placeholders[index]

    def replace(self, inputs):
        for old, new in zip(self, inputs):
            old.replace(new)


def shuffle_right(word, amount):
    """ shuffle a word right (x2) adding 0's to the left """
    network = word[0].network
    res = [Tie(network, False) for i in range(amount)] + word
    if amount:
        carry = Or(*res[len(word) :])
    else:
        carry = Tie(network, False)
    return res[: len(word)], carry
