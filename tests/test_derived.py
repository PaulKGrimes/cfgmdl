#!/usr/bin/env python
"""
Test the model build
"""
from cfgmdl import Model, Parameter, Property, Derived, cached

from collections import OrderedDict as odict


def test_derived():

    class TestClass(Model):

        x = Property(dtype=float, default=1., help='variable x')
        y = Property(dtype=float, default=2., help='variable y')
        z = Property(dtype=float, required=True, help='variable y')
        der = Derived(dtype=float, format='%.1f', uses=[x,y,z], help="A derived parameter")
        der2 = Derived(dtype=float, format='%.1f', loadername="_loader2", uses=[x,y,z], help="A derived parameter")
        der3 = Derived(dtype=float, format='%.1f', loadername="_loader3", uses=[], help="A derived parameter")    

        @cached(uses=[x, y, z])
        def f(self):
            return self.x + self.y + self.z        
        
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

    assert test_obj.f == 6
    
    assert test_obj.der2 == 12.

    try: test_obj.der3
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in Derived.__get__")

    test_obj.x = 2.
    assert test_obj.der == 7.
    assert test_obj.f== 7
    
    test_obj.der = 9.
    assert test_obj.der == 9.

    del test_obj.der
    assert test_obj.der == 7
    
    del test_obj.x
    assert test_obj.der == 6.

    del test_obj.der
    assert test_obj._der is None

    try:
        class TestClass(Model):        
            g = 7
            der = Derived(dtype=float, format='%.1f', loader=g, help="A derived parameter")
        test_obj = TestClass()
        test_obj.der
    except RuntimeError: pass
    else: raise RuntimeError("Failed to catch ValueError in Derived.loader")

    try:
        class TestClass(Model):
            g = 7
            der = Derived(dtype=float, format='%.1f', loadername="g", help="A derived parameter")
        test_obj = TestClass()
        test_obj.der
    except RuntimeError: pass
    else: raise RuntimeError("Failed to catch ValueError in Derived.loader")

