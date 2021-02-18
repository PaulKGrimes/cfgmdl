#!/usr/bin/env python
"""
Test the model build
"""
from cfgmdl import Model, Parameter, Property, Derived, Choice

from collections import OrderedDict as odict


def test_derived():

    class TestClass(Model):
        
        x = Property(dtype=float, default=1., help='variable x')
        y = Property(dtype=float, default=2., help='variable y')
        z = Property(dtype=float, required=True, help='variable y')
        der = Derived(dtype=float, format='%.1f', help="A derived parameter")
        der2 = Derived(dtype=float, format='%.1f', loader="_loader2", help="A derived parameter")
        der3 = Derived(dtype=float, format='%.1f', loader="_loader3", help="A derived parameter")    
        
        def _load_der(self):
            dummy = 1.
            return dummy * self.x + self.y + self.z

        def _loader2(self):
            return 2. * (self.x + self.y + self.z)
    
        def _loader3(self):
            return "aa"

    test_obj = TestClass(z=3.)

    assert test_obj._der is None    

    assert test_obj.der == 6.
    assert test_obj.der == 6
    
    assert test_obj.der2 == 12.

    try: test_obj.der3
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in Derived.__get__")

    test_obj.x = 2.
    assert test_obj.der == 7.

    test_obj.der = 9.
    assert test_obj.der == 9.

    del test_obj.der
    assert test_obj.der == 7
    
    del test_obj.x
    assert test_obj.der == 6.

    del test_obj.der
    assert test_obj._der is None

    
    class TestClass(Model):        
        g = 7
        der = Derived(dtype=float, format='%.1f', loader=g, help="A derived parameter")

    try: test_obj = TestClass()
    except ValueError: pass
    else: raise ValueError("Failed to catch ValueError in Derived.loader")
