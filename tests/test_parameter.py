#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

from cfgmdl import Model, Parameter

from collections import OrderedDict as odict

def test_parameter():
    try:
        class TestClass(Model):
            vv = Parameter(dummy=3)
    except AttributeError: pass
    else: raise AttributeError("Failed to catch AttributeError")

    class TestClass(Model):
        vv = Parameter()

    test_obj = TestClass()
    assert np.isnan(test_obj.vv)
    test_obj.vv = 0.3
    assert test_obj.vv == 0.3
    test_obj.vv = [0.3, 0.2, 0.4]
    assert np.allclose(test_obj.vv, [0.3, 0.2, 0.4])

    help(test_obj.getp('vv'))
    #test_obj.getp('vv').dump()
    
    class TestClass(Model):
        vv = Parameter(default=0.3)

    test_obj = TestClass()
    assert test_obj.vv == 0.3
    test_obj.vv = 0.4
    assert test_obj.vv == 0.4
    test_obj.vv = [0.3, 0.2, 0.4]
    assert np.allclose(test_obj.vv, [0.3, 0.2, 0.4])

    test_obj.vv += 0.1
    assert np.allclose(test_obj.vv, [0.4, 0.3, 0.5])

    test_obj = TestClass(vv=[0.3, 0.2, 0.4])    
    assert np.allclose(test_obj.vv, [0.3, 0.2, 0.4])

    test_obj.vv += 0.1
    assert np.allclose(test_obj.vv, [0.4, 0.3, 0.5])
