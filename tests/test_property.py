#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

from cfgmdl import Model, Property

from collections import OrderedDict as odict

from cfgmdl import Unit
Unit.update(dict(mm=1e-3))


def check_property(dtype, default, test_val, bad_val=None, cast_val=None, test_unit=None):

    class TestClass(Model):
        v = Property(dtype=dtype, default=default, help="A Property")
        v2 = Property(dtype=dtype, help="A Property")
        v3 = Property(dtype=dtype, required=True, help="A Property")
        v4 = Property(dtype=dtype, default=test_val, help="A Property", unit=test_unit)

    try: bad = TestClass()
    except ValueError: pass
    else: raise ValueError("Failed to catch ValueError for missing required Property")
            
    test_obj = TestClass(v3=default)
    assert test_obj.v == default
    assert test_obj.v2 is None

    if test_unit:
        assert np.allclose(test_obj.v4, test_unit(test_val))
    else:
        assert test_obj.v4 == test_val
    
    assert test_obj._properties['v'].default_prefix == ""
    assert test_obj._properties['v'].default_value('dtype') is None

    
    test_obj.v = test_val
    assert test_obj.v == test_val

    test_obj.v = None
    assert test_obj.v is None

    test_obj.v2 = test_val
    assert test_obj.v2 == test_val

    delattr(test_obj, 'v')
    assert test_obj.v == default
    test_obj.v = test_val
    assert test_obj.v == test_val

    del test_obj.v
    assert test_obj.v == default
    test_obj.v = test_val
    assert test_obj.v == test_val
    
    setattr(test_obj, 'v', default)
    assert test_obj.v == default
    assert test_obj.v2 == test_val

    assert getattr(test_obj, 'v') == default

    if cast_val is not None:
        test_obj.v = cast_val
        assert test_obj.v == dtype(cast_val)

        test_obj.v = default
        assert test_obj.v == default
        
        setattr(test_obj, 'v', cast_val)
        assert test_obj.v == dtype(cast_val)
    
    if bad_val is not None:

        try: test_obj.v = bad_val
        except TypeError: pass
        else: raise TypeError("Failed to catch TypeError in CheckProperty")
        
        try: test_obj.v2 = bad_val
        except TypeError: pass
        else: raise TypeError("Failed to catch TypeError in CheckProperty")

        try: test_obj.v3 = bad_val
        except TypeError: pass
        else: raise TypeError("Failed to catch TypeError in CheckProperty")

        try: bad = TestClass(v3=bad_val)
        except TypeError: pass
        else: raise TypeError("Failed to catch TypeError in Model.set_attributes")

        if dtype == dict:
            return

        try: bad = TestClass(v3=dict(value=bad_val))
        except TypeError: pass
        else: raise TypeError("Failed to catch TypeError in Model.set_attributes")

    
def test_property_basics():
    
    try:
        class TestClass(Model):
            vv = Property(dummy=3)
    except AttributeError: pass
    else: raise AttributeError("Failed to catch AttributeError")

    class TestClass(Model):
        vv = Property()

    test_obj = TestClass()
        
    help(test_obj._vv)

    
def test_property_none():
    check_property(None, None, None)
    
def test_property_string():
    check_property(str, "aa", "ab")

def test_property_int():
    check_property(int, 1, 2, "aa", test_unit=Unit('mm'))

def test_property_float():
    check_property(float, 1., 2., "aa", 1, test_unit=Unit('mm'))

def test_property_list():
    check_property(list, [], [3, 4], None, (3, 4), test_unit=Unit('mm'))

def test_property_dict():
    check_property(dict, {}, {3:4})

