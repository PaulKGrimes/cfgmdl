#!/usr/bin/env python
""" Tools wrap functions with jax methods for automatic differentiation
"""
import numpy as np

from collections.abc import Iterable

from jax import grad, jacfwd, jacrev
import jax.numpy as jnp


def check_inputs(x, inputs):
    """Convert inputs to arrays"""
    ret = []
    if x is None:
        x = np.nan
    elif not isinstance(x, (Iterable, int, float)):
        raise TypeError("Non-numeric value %s passed in Physics" % (str(x)))

    x = np.array(x).astype(np.float)
    ret.append(x)
    if not inputs:
        return ret

    for inp in inputs:
        if callable(inp):
            ret.append(inp(x).astype(np.float))
        elif inp is None:
            ret.append(np.full(x.shape, np.nan))
        elif isinstance(inp, (Iterable, int, float)):
            ret.append(np.array(inp).astype(np.float))
        else:
            raise TypeError("Non-numeric value %s passed in Physics" % (str(x)))
    return ret


def jax_hess(ifunc, argnums):
    """Return the hessian of a function

    Parameter
    ---------
    ifunc : `function`
        The inner function being wrapped
    argnum : `int` or `tuple`
        Indices of the arguments to get derivatvies for

    Return
    ------
    hess : `array`
        The Hessian matrix
    """
    return jacfwd(jacrev(ifunc, argnums), argnums)

def jax_wrapper(wfunc, ifunc, getargs, varidx, *args, **kwds):
    """Wrap a function with a jax function

    Parameter
    ---------
    wfunc : `function`
        The `jax` function to wrap with
    ifunc : `function`
        The inner function being wrapped
    getargs : `function`
        A function that formats the arguments to the ifunc
    varidx : `dict`
        Dictionary mapping variable names to indices

    Keywords
    --------
    argnums : `int` or `tuple`
        Indices of the arguments to get derivatives for
    argnames : `list`
        Names of the arguments to get derivatives for

    Return
    ------
    func : `function`
        The wrapped function

    Notes
    -----
    Get args should return a 2-D array, each row consisting a set of argument to the inner function

    args and kwds are passes to the getargs function
    """
    argnums = kwds.get('argnums', 0)
    argnames = kwds.get('argnames', None)
    if argnames is not None:
        argnums = [ varidx[argname] for argname in argnames ]
    args_ = getargs(*args, **kwds)
    wrapped = wfunc(ifunc, argnums)
    return jnp.array([wrapped(*args__) for args__ in args_])


class Function:
    """Decorator class to functions to add gradient, hessians to a functin

    Examples::

        class MyClass(Model):

            var1 = Parameter(default=0.3, help="A variable")
            var2 = Parameter(default=1.2, help="Another variable")

            @Function
            def product(extra_var, var1, var2):
                return extra_var*var1*var2

        # Make an object
        my_obj = MyClass()

        # Get the product, note that extra_var must be provied, but var1 and var2 are taken from the class
        my_obj.product(1.)

        # Get the product, overrided var1
        my_obj.product(1., var1=0.4)

        # Get the gradient for variable 0 (i.e., extra_var), evaluated at extra_var = 1.
        my_obj.product.grad(1.)

        # Get the gradient for variables 0,1,2, evaluated at extra_var = 1.
        my_obj.product.grad(1., argnums=[0,1,2])

        # Get the gradient for var1, var2, evaluated at extra_var = 1.
        my_obj.product.grad(1., argnames=["var1", "var2"])

        # Get the gradient for variable 0, evaluated at several points
        my_obj.product.grad([1.,1.2.,1.3])

        # Get the gradient for variables 0,1,2, evaluated at several points
        my_obj.product.grad(1., argnums=[0,1,2])

    """
    def __init__(self, func):
        """Constructor, wraps `func`"""
        self._func = func
        self._obj = None
        self._varnames = func.__code__.co_varnames[:func.__code__.co_argcount]
        self._defaults = func.__defaults__
        self.varidx = {}
        for i, varname in enumerate(self._varnames):
            self.varidx[varname] = i

    def __get__(self, instance, _owner):
        """Hook to connect this wrapper to the instance that has the wrapped member function"""
        self._obj = instance
        return self

    def __call__(self, *args, **kwds):
        """Call the wrapped function"""
        args_ = self.get_args(*args, **kwds)
        return jnp.array([self._func(*args__) for args__ in args_])

    @property
    def func(self):
        """Return the inner function"""
        return self._func

    def get_args(self, *args, **kwds):
        """Get the arguments"""
        #use_args = [arg for arg in args]
        use_args = list(args)
        nargs = len(use_args)
        for varname in self._varnames[nargs:]:
            use_args.append(kwds.get(varname, getattr(self._obj, varname)))
        if len(use_args) != self._func.__code__.co_argcount:
            raise ValueError("Only found %i arguments, need %i" % (len(use_args), self._func.__code__.co_argcount))
        arrays_in = check_inputs(use_args[0], use_args[1:])
        aa = np.broadcast(*arrays_in)
        if not aa.nd:
            return np.expand_dims(arrays_in, 0)
        return aa

    def grad(self, *args, **kwds):
        """Return the gradient"""
        return jax_wrapper(grad, self._func, self.get_args, self.varidx, *args, **kwds)

    def jacfwd(self, *args, **kwds):
        """Return the jacobian"""
        return jax_wrapper(jacfwd, self._func, self.get_args, self.varidx, *args, **kwds)

    def jacrev(self, *args, **kwds):
        """Return the jacobian"""
        return jax_wrapper(jacrev, self._func, self.get_args, self.varidx, *args, **kwds)

    def hess(self, *args, **kwds):
        """Return the hessian"""
        return jax_wrapper(jax_hess, self._func, self.get_args, self.varidx, *args, **kwds)
