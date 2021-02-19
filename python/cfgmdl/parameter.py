#!/usr/bin/env python
""" Tools to manage Property object that can be used as fit parameters.
"""
from copy import deepcopy
from collections.abc import Mapping

import numpy as np

from .utils import defaults_decorator
from .property import Property
from .param_holder import ParamHolder


class Parameter(Property):
    """Property sub-class for defining a numerical Parameter.

    This includes value, bounds, error estimates and fixed/free status
    (i.e., for fitting)

    """

    # Better to keep the structure consistent with Property
    defaults = deepcopy(Property.defaults)
    defaults['bounds'] = (np.nan, 'Allowed bounds for value')
    defaults['errors'] = (np.nan, 'Errors on this parameter')
    defaults['free'] = (False, 'Is this property allowed to vary?')
    defaults['scale'] = (1.0, 'Scale to apply for this property')

    # Overwrite the default dtype
    defaults['dtype'] = (ParamHolder, 'Data type')
    defaults['default'] = (np.nan, 'Default value')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.bounds = np.nan
        self.errors = np.nan
        self.free = False
        self.scale = 1.
        super(Parameter, self).__init__(**kwargs)

    def __set__(self, obj, value):
        """Set the value in the client object

        Parameter
        ---------
        obj : ...
            The client object
        value : ...
            The value being set

        Rasies
        ------
        TypeError : The input value is the wrong type (i.e., not castable to Darray)

        ValueError : The input values fail the bounds check

        Notes
        -----

        If value is a dict, this will use `Darray(**value)` to construct the managed value
        Otherwise this will use Darray(value, **defaults) to construct the managed value
        """
        par = getattr(obj, self.private_name, None)

        if par is None:
            if isinstance(value, Mapping):
                par = self.dtype(**value)
            else:
                par = self.dtype(value=value, bounds=self.bounds, errors=self.errors, scale=self.scale, free=self.free)
        else:
            par.update(value)

        super(Parameter, self).__set__(obj, par)

    def __get__(self, obj, objtype=None):
        """Get the value from the client object

        Parameter
        ---------
        obj : ...
            The client object

        Return
        ------
        out : ...
            The requested value
        """
        val = getattr(obj, self.private_name).__call__()
        if self.unit is None:
            return val
        return self.unit(val) #pylint: disable=not-callable

    def todict(self, obj):
        """Extract values as an odict """
        return getattr(obj, self.private_name).todict()

    def tostr(self, obj):
        """Extract values as a string"""
        return str(getattr(obj, self.private_name))

    def _cast_type(self, value):
        """Hook took override type casting"""
        return value

    def validate_value(self, obj, value): #pylint: disable=unused-argument,no-self-use
        """Validate a value"""
        value.check_bounds()
