#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

import yaml

from cfgmdl import Model, Parameter, Property, Derived, Choice, tools

from collections import OrderedDict as odict


def test_model():

    class Child(Model):

        z = Parameter(help='variable z')

    class test_class(Model):
        pass


    dd = dict(default=dict(z=3), elements=dict(child1=dict(z=4), child2=dict(z=5)))
    
    type_dict = {None:Child}

    tc = tools.build_class("tc", (test_class,), [dd], [type_dict])
    assert tc.child1.z() == 4.
    assert tc.child2.z() == 5.


    dd = dict(child1=dict(z=4), child2=dict(z=5))
    tc2 = tools.build_class("tc2", (test_class,), [dd], [type_dict])

    assert tc2.child1.z() == 4.
    assert tc2.child2.z() == 5.
    
    dd = dict(default=dict(z=3), elements=dict(child1=dict(z=4), child2=None))
    
    tc3 = tools.build_class("tc", (test_class,), [dd], [type_dict])
    assert tc3.child1.z() == 4.
    assert tc3.child2.z() == 3.
