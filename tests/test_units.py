#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

from cfgmdl.unit import Unit


def test_units():

    Unit.update(dict(mm=1e-3))

    one = Unit()
    assert one.name == ''
    assert one(1.) == 1.

    mm = Unit('mm')
    assert mm.name == 'mm'
    assert mm(1.) == 1e-3
    assert mm.inverse(1.) == 1e3

    au = Unit(1e-3)
    assert au.name == 'a.u.'
    assert au(1.) == 1e-3
    assert au.inverse(1.) == 1e3

    try: Unit("ff")
    except KeyError: pass
    else: raise KeyError("Failed to catch KeyError")

    try: Unit([1, 2, 3])
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError")
