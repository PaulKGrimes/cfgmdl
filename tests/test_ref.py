#!/usr/bin/env python
"""
Test the model build
"""
from cfgmdl import Model, Property, Derived, Ref

from collections import OrderedDict as odict


def test_ref():

    class TestClass(Model):
        
        x = Property(dtype=float, default=1., help='variable x')
        y = Property(dtype=float, default=2., help='variable y')
        z = Property(dtype=float, required=True, help='variable y')
        der = Derived(dtype=float, format='%.1f', uses=[x,y,z], help="A derived parameter")
        
        def _load_der(self):
            dummy = 1.
            return dummy * self.x + self.y + self.z

    class OtherClass(Model):

        a = Property(dtype=float, default=3., help='variable a')
        x = Ref()
        z = Ref(attr='z')
        der = Ref(attr='der')
        
        
    test_obj = TestClass(z=3.)
    other_class = OtherClass()

    assert other_class.x is None
    assert other_class.z is None
    assert other_class.der is None

    other_class.x = test_obj
    other_class.z = test_obj
    other_class.der = test_obj

    assert test_obj.x == 1
    assert test_obj.z == 3
    assert other_class.z == 3
    assert other_class.der == 6

    test_obj.x = 2
    assert other_class.der == 7


    del other_class.z
    assert other_class.z is None
