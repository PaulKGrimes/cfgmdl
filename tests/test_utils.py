#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

from cfgmdl.utils import is_none, is_not_none


def test_none():

    assert is_none(None)
    assert is_none('None')
    assert is_none('none')

    assert is_none([]) == False
    assert is_none({}) == False
    assert is_none("a") == False
    
    assert is_not_none(None) == False
    assert is_not_none('None') == False
    assert is_not_none('none') == False

    assert is_not_none([])
    assert is_not_none({})
    assert is_not_none("a")

