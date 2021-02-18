#!/usr/bin/env python
"""
Test the model build
"""
from cfgmdl import Model, Choice


def test_choice():
    try:
        class TestClass(Model):
            vv = Choice(choices=['a','b','c'], default='d')
    except AttributeError: pass
    else: pass #raise AttributeError("Failed to catch AttributeError")

    class TestClass(Model):
        vv = Choice(choices=['a','b','c'], default='a')

    test_obj = TestClass()
    assert test_obj.vv == 'a'
    test_obj.vv = 'b'
    assert test_obj.vv == 'b'

    del test_obj.vv
    assert test_obj.vv == 'a'
    
    try: test_obj.vv = 'd'
    except (TypeError, ValueError): pass
    else: raise ValueError("Failed to catch ValueError in Choice")

    class TestClass(Model):
        vv = Choice(choices=['a','b','c'])

    test_obj = TestClass()
    assert test_obj.vv is None

    test_obj.vv = 'b'
    assert test_obj.vv == 'b'

    del test_obj.vv
    assert test_obj.vv is None

    try: test_obj.vv = "d"
    except (TypeError, ValueError): pass
    else: raise TypeError("Failed to catch ValueError in Choice")
        
    help(test_obj.getp('vv'))
    #test_obj.getp('vv').dump()
