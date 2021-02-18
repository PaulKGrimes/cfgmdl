#!/usr/bin/env python
"""
Test the model build
"""
import numpy as np
import jax.numpy as jnp

from cfgmdl import Model
from cfgmdl import Property, Parameter, Function

from collections import OrderedDict as odict

class TestModel(Model):
    """
    Foreground model base class
    """    
    v1 = Property(dtype=float, default=3., format="%.2e")
    v2 = Parameter(default=2., bounds=[0., 3.], errors=[0.1, 0.3], free=True)
    v3 = Parameter(default=3.)
    
    @Function
    def ff(e1, e2, v1, v2, v3):
        vv1 = e1 * e2
        vv2 = (v1 / v2)**v3
        vv3 = vv1 * v2
        # Convert brightness temperature [K_RJ] to physical temperature [K]
        return vv3*v1

    @Function
    def sinv1(v1):
        return jnp.sin(v1)

    
def test_function():

    a = TestModel()
    assert a.ff(1., 1.) == 6.
    assert a.ff.grad(1., 1.) == 6.
    assert a.ff.hess(1., 1.) == 0.

    try: a.ff(1.)
    except AttributeError: pass
    else: raise AttributeError("Failed to catch AttributeError in Function.get_args()")

    try: a.ff(1., 2., 3., 4, 5., 6.)
    except ValueError: pass
    else: raise Value("Failed to catch AttributeError in Function.get_args()")

    try: a.ff('as', 1.)
    except ValueError: pass
    else: raise ValueError("Failed to catch ValueError in check_inputs")

    try: a.ff(type(int), 1.)
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in check_inputs")

    try: a.ff(1., a)
    except TypeError: pass
    else: raise TypeError("Failed to catch TypeError in check_inputs")

    assert jnp.isnan(a.ff(1., None)[0]).all()
        
    assert a.ff(1., 1.) == a.ff.func(1., 1., 3., 2., 3)

    assert a.ff(2., jnp.sqrt) == a.ff.func(2., jnp.sqrt(2.), 3., 2., 3.)
    
    assert a.ff.grad(1., 1.) == a.ff.jacrev(1., 1.)
    assert a.ff.grad(1., 1.) == a.ff.jacfwd(1., 1.)
    
    assert np.allclose(a.ff([1.,2.], 1.), [6., 12.])
    assert np.allclose(a.ff([1.,2.], [1., 2]), [6, 24])

    assert (a.ff.grad(1., 1., argnums=[2,3,4]) == a.ff.grad(1., 1., argnames=['v1', 'v2', 'v3'])).all()

    assert a.sinv1() == np.sin(a.v1)

    
    
    
    
    
