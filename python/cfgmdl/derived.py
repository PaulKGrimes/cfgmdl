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
    defaults['loader'] = (None, 'Function to load datum')

    @classmethod
    def dummy(cls): #pragma: no cover
        """Dummy function"""
        return

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.loader = self.dummy
        super(Derived, self).__init__(**kwargs)

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

        times = [ getattr(obj, "_%s_timestamp" % vn, 0.) for vn in loader.__func__.__code__.co_names ]
        if times:
            ts_max = np.max(times)
        else:
            ts_max = 0.
        my_ts = getattr(obj, self.time_name, -1.)

        if my_ts > ts_max and val is not None:
            return val
        val = loader()
        self.__set__(obj, val)
        return getattr(obj, self.private_name)
