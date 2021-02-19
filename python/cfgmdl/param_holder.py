#!/usr/bin/env python
""" Tools to manage Property object that can be used as fit parameters.
"""
from collections.abc import Mapping
import numpy as np

from .array import Array
from .configurable import Configurable

class ParamHolder(Configurable):
    """Wrapper around a data value

    This includes value, bounds, error estimates and fixed/free status
    (i.e., for fitting)

    """
    value = Array(help='Parameter Value')
    errors = Array(help='Parameter Uncertainties')
    bounds = Array(help='Parameter Bounds')
    scale = Array(default=1., help='Paramter Scale Factor')
    free = Array(dtype=bool, default=False, help='Free/Fixed Flag')

    def __init__(self, *args, **kwargs):
        """Constructor"""
        kwcopy = kwargs.copy()
        if args: #pragma: no cover
            if 'value' in kwcopy:
                raise ValueError("value keyword provided in addition to arguments")
            kwcopy['value'] = args
        super(ParamHolder, self).__init__(**kwargs)
        self.check_bounds()

    def __str__(self, indent=0):
        """Return self as a string"""
        return '{0:>{2}}{1}'.format('', '', indent) + "{_value} += {_errors} [{_bounds}] <{_scale}> {_free}".format(**self.__dict__)

    def update(self, *args, **kwargs):
        """Update the parameter"""
        kwcopy = kwargs.copy()
        if args:
            if 'value' in kwcopy:
                raise ValueError("value keyword provided in addition to arguments")
            if len(args) > 1:
                raise ValueError("Only 1 argument allowed")
            if isinstance(args[0], Mapping):
                kwcopy.update(**args[0])
            else:
                kwcopy['value'] = args[0]
        super(ParamHolder, self).update(**kwcopy)
        self.check_bounds()

    def check_bounds(self):
        """Hook for bounds-checking, invoked during assignment.

        raises ValueError if value is outside of bounds.
        does nothing if bounds is set to None.
        """
        if np.isnan(self.value).all():
            return
        if np.isnan(self.bounds).all():
            return
        if np.bitwise_or(self.value < self.bounds[0], self.value > self.bounds[-1]).any(): #pylint: disable=unsubscriptable-object
            raise ValueError("Value outside bounds: %.s [%s,%s]" % (self.value, self.bounds[0], self.bounds[-1])) #pylint: disable=unsubscriptable-object

    def __call__(self):
        """Return the product of the value and the scale"""
        return self.value * self.scale
