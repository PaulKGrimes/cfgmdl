#!/usr/bin/env python
""" Tools to manage array propery objects.
"""
from copy import deepcopy

import numpy as np

from .property import Property, defaults_decorator

class Array(Property):
    """Property sub-class numpy arrays
    """
    defaults = deepcopy(Property.defaults)
    defaults['dtype'] = (float, 'Data type of array element')
    defaults['default'] = (np.nan, 'Default value')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        super(Array, self).__init__(**kwargs)

    def _cast_type(self, value):
        """Hook took override type casting"""
        return np.array(value).astype(self.dtype)
