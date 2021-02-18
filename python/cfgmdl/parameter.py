#!/usr/bin/env python
""" Tools to manage Property object that can be used as fit parameters.
"""
from copy import deepcopy
from collections import OrderedDict as odict

from .property import Property, defaults_decorator

import numpy as np


class Parameter(Property):
    """Property sub-class for defining a numerical Parameter.

    This includes value, bounds, error estimates and fixed/free status
    (i.e., for fitting)

    """

    # Better to keep the structure consistent with Property
    defaults = deepcopy(Property.defaults) + [
        ('bounds', np.nan, 'Allowed bounds for value'),
        ('errors', np.nan, 'Errors on this parameter'),
        ('free', False, 'Is this property allowed to vary?'),
        ('scale', 1.0, 'Scale to apply for this property'),
    ]
    # Overwrite the default dtype
    idx = [d[0] for d in defaults].index('dtype')
    defaults[idx] = ('dtype', np.ndarray, 'Data type')
    idx = [d[0] for d in defaults].index('default')
    defaults[idx] = ('default', np.nan, 'Default value')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.bounds_name = None
        self.errors_name = None
        self.free_name = None
        self.scale_name = None
        super(Parameter, self).__init__(**kwargs)

    def __set_name__(self, owner, name):
        """Set the name of the privately managed value"""
        super(Parameter, self).__set_name__(owner, name)
        self.bounds_name = '_' + name + '_bounds'
        self.errors_name = '_' + name + '_errors'
        self.free_name = '_' + name + '_free'
        self.scale_name = '_' + name + '_scale'

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
        if not isinstance(value, dict):
            value = dict(value=value)
        else:
            value.setdefault('value', getattr(obj, self.private_name, None))

        for key in ['bounds', 'errors', 'scale', 'free']:
            hidden_name = "_%s_%s" % (self.public_name, key)
            if not hasattr(obj, hidden_name):
                cast_val = getattr(self, key)
            else:
                if key not in value:
                    continue
                try:
                    if key in ['free']:
                        cast_val = np.array(value[key]).astype(bool)
                    else:
                        cast_val = np.array(value[key]).astype(float)
                except ValueError as msg:
                    raise ValueError("Failed to set %s: not %s castable as array" % (hidden_name, value[key])) from msg
            setattr(obj, hidden_name, cast_val)

        super(Parameter, self).__set__(obj, value['value'])


    def validate_value(self, obj, value):
        """Validate a value

        In this case this does type-checking and bounds-checking

        Rasies
        ------
        TypeError : The input value is the wrong type (i.e., not float or float64)

        ValueError : The input values fail the bounds check
        """
        self.check_bounds(obj, value)

    def todict(self, obj):
        """Extract values as an odict """
        return odict([('value', np.array(getattr(obj, self.private_name)))] +
                         [(key, getattr(obj, "_%s_%s" % (self.public_name, key), None)) for key in ['bounds', 'errors', 'free', 'scale']])

    def tostr(self, obj):
        """Extract values as a string"""
        ret = str(getattr(obj, self.private_name))
        errors = getattr(obj, self.errors_name, None)
        bounds = getattr(obj, self.bounds_name, None)
        scale = getattr(obj, self.scale_name, None)
        free = getattr(obj, self.free_name, None)

        ret += ' +- %s' % errors
        ret += ' [%s]' % bounds
        ret += ' <%s>' % scale
        ret += ' %s' % free
        return ret

    def symmetric_error(self, obj):
        """Return the symmertic error
        """
        errors = getattr(obj, self.errors_name, None)
        errors = np.array(errors)
        if not errors.shape:
            return errors
        if errors.shape[0] == 2:
            return 0.5 * (errors[0] + errors[1])
        return errors

    def check_bounds(self, obj, value):
        """Bounds checking"""
        bounds = getattr(obj, self.bounds_name)
        if np.isnan(bounds).all():
            return
        if np.any(value < bounds[0]) or np.any(value > bounds[1]):
            msg = "Value outside bounds: %.2g [%.2g,%.2g]" % (value, bounds[0], bounds[1])
            raise ValueError(msg)


    def _cast_type(self, value):
        """Hook took override type casting"""
        return np.array(value).astype(float)
