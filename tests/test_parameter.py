#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np
from collections import OrderedDict as odict

from cfgmdl import Model, Parameter, Unit
Unit.update(dict(mm=1e-3))


def test_parameter():
    try:
        class TestClass(Model):
            vv = Parameter(dummy=3)
    except AttributeError: pass
    else: raise AttributeError("Failed to catch AttributeError")

    class TestClass(Model):
        vv = Parameter()

    test_obj = TestClass()
    assert np.isnan(test_obj.vv())

    import pdb
    #pdb.set_trace()
    test_obj.vv = 0.3
    assert test_obj.vv() == 0.3
    test_obj.vv = [0.3, 0.2, 0.4]
    assert np.allclose(test_obj.vv(), [0.3, 0.2, 0.4])

    help(test_obj._vv)
    
    class TestClass(Model):
        vv = Parameter(default=0.3)    
        vv2 = Parameter(default=0.3, unit=Unit('mm'))
        
    test_obj = TestClass()

    assert test_obj.vv() == 0.3
    test_obj.vv = 0.4
    assert test_obj.vv() == 0.4

    test_obj.vv.set_from_SI(0.3)
    assert test_obj.vv() == 0.3

    test_obj.vv = [0.3, 0.2, 0.4]
    assert np.allclose(test_obj.vv(), [0.3, 0.2, 0.4])

    test_obj.vv.value += 0.1
    assert np.allclose(test_obj.vv(), [0.4, 0.3, 0.5])

    assert test_obj.vv2() == Unit('mm')(0.3)
    assert test_obj.vv2.SI == Unit('mm')(0.3)
    assert test_obj.vv2.value == 0.3

    test_obj.vv2.set_from_SI(Unit('mm')(0.3))
    assert test_obj.vv2.value == 0.3

    try: test_obj._vv.update(3.3, value=3.3)
    except ValueError: pass
    else: raise ValueError("Failed to catch value error")

    try: test_obj._vv.update(3.3, 5.3)
    except ValueError: pass
    else: raise ValueError("Failed to catch value error")

    test_obj._vv.update(dict(value=3.3))
    assert test_obj.vv() == 3.3
    
    test_obj = TestClass(vv=[0.3, 0.2, 0.4])    
    assert np.allclose(test_obj.vv(), [0.3, 0.2, 0.4])

    test_obj.vv.value += 0.1
    assert np.allclose(test_obj.vv(), [0.4, 0.3, 0.5])

    class TestClass(Model):
        vv = Parameter(default=(3.3))
        vv2 = Parameter(default=None)
        
    test_obj = TestClass(vv=3.5)
    assert test_obj.vv() == 3.5

    assert np.isnan(test_obj.vv2()).all()

    test_obj.vv2 = 3.5
    assert test_obj.vv2() == 3.5


    
