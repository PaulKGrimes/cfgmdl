#!/usr/bin/env python
"""
Classes used to describe aspect of Models.

The base class is `Property` which describes any one property of a model,
such as the name, or some other fixed property.

The `Parameter` class describes variable model parameters.

The `Derived` class describes model properies that are derived
from other model properties.

"""
from collections import OrderedDict as odict

import numpy as np

from .configurable import Configurable
from .parameter import Parameter

class Model(Configurable):
    """Configurable model with parameter management

    """
    def __init__(self, **kwargs):
        """ C'tor.  Build from a set of keyword arguments.
        """
        super(Model, self).__init__(**kwargs)
        self._params = self.find_params()

    @classmethod
    def find_params(cls):
        """Find properties that belong to this model"""
        the_classes = cls.mro()
        params = odict()
        for the_class in the_classes:
            for key, val in the_class.__dict__.items():
                if isinstance(val, Parameter):
                    params[key] = val
        return params


    def get_params(self, pnames=None):
        """ Return a list of Parameter objects

        Parameters
        ----------

        pname : list or None
           If a list get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------

        params : list
            list of Parameters

        """
        l = []
        if pnames is None:
            pnames = self._params.keys()
        for pname in pnames:
            p = self._params[pname]
            if isinstance(p, Parameter):
                l.append(p)
        return l

    def param_values(self, pnames=None):
        """ Return an array with the parameter values

        Parameters
        ----------

        pname : list or None
           If a list, get the values of the `Parameter` objects with those names

           If none, get all values of all the `Parameter` objects

        Returns
        -------

        values : `np.array`
            Parameter values

        """
        l = self.get_params(pnames)
        v = [p.__get__(self) for p in l]
        return np.array(v)


    def param_str(self, pnames=None):
        """ Return an string with the parameter values

        Parameters
        ----------

        pname : list or None
           If a list, get the values of the `Parameter` objects with those names

           If none, get all values of all the `Parameter` objects

        Returns
        -------

        s : `str`
            Parameter value string
        """
        l = self.get_params(pnames)
        s = ""
        for p in l:
            s += "%s : %s\n" % (p.public_name, p.tostr(self))
        return s
