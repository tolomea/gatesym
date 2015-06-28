from __future__ import unicode_literals, division, absolute_import

from gatesym import core, gates
from gatesym.blocks import adders


def test_get():
    n = core.Network()
    a = gates.Tie(n)
    b = gates.Tie(n)
    c = gates.Tie(n)
    r, co = adders.full_adder(a, b, c)
    assert a.get("full_adder.half_adder.and.half_adder.or.full_adder") is co
    assert a.get("full_adder.half_adder.not.and.or.half_adder.half_adder.not.and.or.half_adder.full_adder") is r


def test_list():
    n = core.Network()
    a = gates.Tie(n)
    b = gates.Tie(n)
    c = gates.Tie(n)
    r, co = adders.full_adder(a, b, c)
    assert a.list("") == ["full_adder"]
    assert a.list("full_adder") == ["half_adder"]
    assert a.list("full_adder.half_adder") == ["and", "and", "not"]
    assert a.list("full_adder.half_adder.and") == ["half_adder"]
    assert a.list("full_adder.half_adder.and.half_adder") == ["or"]
    assert a.list("full_adder.half_adder.and.half_adder.or") == ["full_adder"]
    assert a.list("full_adder.half_adder.and.half_adder.or.full_adder") == []
