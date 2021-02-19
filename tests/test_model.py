#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np

import yaml

from cfgmdl import Model, Parameter, Property, Derived, Choice

from collections import OrderedDict as odict


def test_model():

    class Parent(Model):

        x = Parameter(default=1., help='variable x')
        y = Parameter(default=2., bounds=[0.,10.], help='variable y')

    class Child(Parent):

        z = Parameter(help='variable z')

    class test_class(Model):

        req = Property(dtype=float, format='%.1f', required=True, help="A required parameter")
        opt = Property(dtype=float, format='%.1f', default=1.0, help="An optional parameter")
        var = Parameter(default=1.0, bounds=[0., 3.], errors=[0.1, 0.3], free=True, help="A variable parameter")
        var2 = Parameter(default=1.0, free=False, help="A fixed parameter")
        der = Derived(dtype=float, format='%.1f', help="A derived parameter")

        def _load_der(self):
            return self.req * self.opt * self.var


    a = Parent()
    assert a.x == 1.
    assert a.y == 2.

    a.x = 3.
    a.y = 4.

    b = Child()
    assert b.x == 1.
    assert b.y == 2.
    assert np.isnan(b.z)
    b.z = 100.
    assert b.z == 100.

    b.update(z=40.)
    assert b.z == 40.

    b.update(z=dict(free=True))
    assert b._z.free

    try: b.update(z=dict(bounds="aa"))
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in Parameter.__set__")

    t = test_class(req=2.,var=2.)

    t_str = str(t)

    dd = t.todict()

    print(dd)
    t_copy = test_class(**dd)

    assert t_copy.var == t.var
    assert t_copy.req == t.req
    assert t_copy.opt == t.opt    

    dd['var'] = 1.5
    t_copy.update(**dd)
    assert t_copy.var == 1.5

    try: t_copy.update(aa=15.)
    except KeyError: pass
    else: raise KeyError("Failed to catch KeyError in Model.update")

    try: t_copy.update(15.)
    except ValueError: pass
    else: raise ValueError("Failed to catch ValueError in Model.update")
        
    try: t_copy.update(var=15.)
    except ValueError: pass
    else: raise ValueError("Failed to catch ValueError in Model.update %s" % t_copy._var)

    t.update(var=dict(errors=0.1))
    assert np.allclose(t._var.errors, 0.1)

    t.update(var=dict(errors=[0.1, 0.2, 0.3]))
    assert np.allclose(t._var.errors, [0.1, 0.2, 0.3])
    
    test_val = t.req * t.opt * t.var
    check = t.der
    assert check==test_val

    t.req = 4.
    check = t.der
    assert check==8.

    try:
        t2 = test_class(var=2.)
        check = t.der
        assert False
    except ValueError:
        pass

    try: a.f == 2
    except AttributeError: pass
    else: raise TypeError("Failed to catch AttributeError in Model.__getatt__")

    params = a.get_params()
    assert len(params) == 2

    params = a.get_params(['x'])
    assert len(params) == 1

    vals = a.param_values()
    assert len(vals) == 2
    assert vals[0] == 3.

    vals = a.param_values(['x'])
    assert len(vals) == 1
    assert vals[0] == 3.

    assert np.isnan(a._x.errors)

    assert np.isnan(a._x.bounds)

    assert np.allclose(a._x.scale, 1)

    assert not a._x.free

    a_dict = a.todict()
    a_str = str(a)
    a_yaml = yaml.dump(a_dict)
    a_pstr = a.param_str()
    print(a_pstr)
    
    for key in ['x', 'y']:
        assert key in a_dict
        assert a_str.index(key) >= 0
        assert a_yaml.index(key) >= 0
        assert a_pstr.index(key) >= 0

        
    try: a.x = 'afda'
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in Model.__set__")

    aa = Child(x=2.)
    aa.x == 2

    aa = test_class(req=5.3)
    assert aa.req == 5.3

    try: bad = test_class(req="aa")
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in Model.update")

    try: bad = Child(vv=dict(value=3))
    except KeyError: pass
    else: raise KeyError("Failed to catch KeyError in Model.set_attributes")


        

def test_property_model():
    class Inner(Model):
        v = Property(dtype=float, default=1., help="A Property")
        v2 = Property(dtype=float, default=2., help="A Property")
        v3 = Property(dtype=float, default=3., help="A Property")
        der = Derived(dtype=float, format='%.1f', help="A derived parameter")

        def _load_der(self):
            return self.v + self.v2 + self.v3

    class TestClass(Model):
        p1 = Property(dtype=Inner, default=Inner())
        p2 = Property(dtype=Inner, default=Inner())
        px = Parameter()
        der = Derived(dtype=float, format='%.1f', help="A derived parameter")

        def _load_der(self):
            return self.p1.der + self.p2.der


    def extract_vals(test_obj):
        return [test_obj.p1.v, test_obj.p1.v2, test_obj.p1.v3, test_obj.p1.der,
                    test_obj.p2.v, test_obj.p2.v2, test_obj.p2.v3, test_obj.p2.der,
                    test_obj.der]

    def assert_vals(test_obj, check_vals):
        vals = extract_vals(test_obj)
        assert np.allclose(vals, check_vals)


    test_obj = TestClass()

    check_vals = np.array([1., 2., 3., 6., 1., 2., 3., 6., 12.])
    assert_vals(test_obj, check_vals)

    test_obj.p1.v += 1.
    check_vals[0] += 1.
    check_vals[3] += 1.
    check_vals[8] += 1.
    assert_vals(test_obj, check_vals)

    test_obj.p2.v += 1.
    check_vals[4] += 1.
    check_vals[7] += 1.
    check_vals[8] += 1.
    assert_vals(test_obj, check_vals)

    dd = test_obj.todict()
    test_copy = TestClass(**dd)

    assert np.allclose(extract_vals(test_obj), extract_vals(test_copy))
    
    test_obj.update(px=3.3)
    assert test_obj.px == 3.3

    test_obj.update(px=[3.3, 3.4])
    assert np.allclose(test_obj.px, [3.3, 3.4])
