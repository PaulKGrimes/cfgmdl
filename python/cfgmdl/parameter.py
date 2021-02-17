#!/usr/bin/env python
""" Tools to manage Property object that can be used as fit parameters.
"""
from copy import deepcopy
from collections import OrderedDict as odict

from .utils import is_none, is_not_none
from .property import Property, defaults_decorator
from .darray import Darray

import numpy as np
import yaml


class Parameter(Property):
    """Property sub-class for defining a numerical Parameter.

    This includes value, bounds, error estimates and fixed/free status
    (i.e., for fitting)

    """

    # Better to keep the structure consistent with Property
    defaults = deepcopy(Property.defaults) + [
        ('bounds', None, 'Allowed bounds for value'),
        ('errors', None, 'Errors on this parameter'),
        ('free', False, 'Is this property allowed to vary?'),
        ('scale', None, 'Scale to apply for this property'),
    ]
    # Overwrite the default dtype
    idx = [d[0] for d in defaults].index('dtype')
    defaults[idx] = ('dtype', Darray, 'Data type')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
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
        val_dict = {}
        for key in ['value', 'bounds', 'errors', 'free', 'scale']:
            if obj is not None:
                obj_val = getattr(obj, key, None)
                if is_not_none(obj_val):
                    val_dict.setdefault(key, obj_val)
            val_dict.setdefault(key, getattr(self, key, None))

        if isinstance(value, dict):
            val_dict.update(value)
        else:
            val_dict.update(dict(value=value))

        try:
            cast_value = self.dtype(**val_dict)  #pylint: disable=no-member
            self.validate_value(cast_value)
        except (TypeError, ValueError) as msg:
            setattr(obj, self.private_name, None)
            raise msg
        setattr(obj, self.private_name, cast_value)

    def validate_value(self, value):
        """Validate a value

        In this case this does bounds-checking, invoked during assignment.

        raises ValueError if value is outside of bounds.
        does nothing if bounds is set to None.
        """
        if is_none(value):
            return
        if value.dtype not in (np.float, np.float64):
            raise TypeError("%s: %s is not a legal parameter Darray type" % (self.private_name, value.dtype))
        value.check_bounds(value)

    def dump(self):
        """Dump this object as a yaml string
        """
        return yaml.dump(self)

    @staticmethod
    def representer(dumper, data):
        """
        http://stackoverflow.com/a/14001707/4075339
        http://stackoverflow.com/a/21912744/4075339
        """
        tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
        return dumper.represent_mapping(
            tag, data.todict().items(), flow_style=True)


def odict_representer(dumper, data):
    """ http://stackoverflow.com/a/21912744/4075339 """
    # Probably belongs in a util
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

yaml.add_representer(odict, odict_representer)
yaml.add_representer(Parameter, Parameter.representer)
