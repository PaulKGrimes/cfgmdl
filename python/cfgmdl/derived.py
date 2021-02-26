#!/usr/bin/env python
""" Tools to manage Property objects that are derived from other Property objects manages by the same client class.
"""

import numpy as np
from copy import deepcopy

from .property import Property, defaults_decorator

class Derived(Property):
    """Property sub-class for derived configuration Properties (i.e., Properties
    that depend on other Properties)

    This allows specifying the specifying a 'loader' function by name
    that is used to compute the value of the property.
    """
    defaults = deepcopy(Property.defaults)
    defaults['loadername'] = (None, 'Name of function to load datum')
    defaults['loader'] = (None, 'Function to load datatum')
    defaults['uses'] = ([], 'Properties used by this one')

    @classmethod
    def dummy(cls): #pragma: no cover
        """Dummy function"""
        return

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.loader = None
        self.loadername = None
        self.uses = []
        super(Derived, self).__init__(**kwargs)

    def __set_name__(self, owner, name):
        """Set the name of the privately managed value"""
        super(Derived, self).__set_name__(owner, name)
        if self.loadername is None:
            if self.loader is not None:
                self.loadername = "_load_%s" % self.loader.__name__
            else:
                self.loadername = "_load_%s" % name
        if self.loader is None:
            loader = getattr(owner, self.loadername, None)
            self.loader = loader
            if not callable(self.loader):
                raise ValueError("Callable loader not defined for Derived object", owner, name, self.loadername, self.loader)
            return
        setattr(owner, self.loadername, self.loader)

    def __get__(self, obj, objtype=None):
        """Get the value from the client object

        Parameter
        ---------
        obj : ...
            The client object

        Return
        ------
        val : ...
            The requested value

        Notes
        -----
        This first checks if the value is cached (i.e., if getattr(obj, self.private_name) is None)

        If it is not cached then it invokes the `self.loader` function to compute the value, and caches the computed value
        """
        val = getattr(obj, self.private_name)

        loader = self.loader

        if loader is None:
            raise ValueError("%s.%s no loader" % (obj, self.public_name))

        ts_check = self.check_timestamp(obj)
        if ts_check and val is not None:
            return val
        val = loader(obj)
        self.__set__(obj, val)
        return getattr(obj, self.private_name)

    def check_timestamp(self, obj):
        """Check if object is up to date w.r.t. to the object it uses"""
        times = [vn.timestamp(obj) for vn in self.uses]
        if times:
            ts_max = np.max(times)
        else:
            ts_max = 0.
        my_ts = self.timestamp(obj)
        return my_ts >= ts_max



def cached(**kwargs):
    """Decorator attach a function to a class as a Derived property
    """
    def decorator(func):
        """Function that appends default kwargs to a function.
        """
        return Derived(loader=func, **kwargs)
    return decorator
