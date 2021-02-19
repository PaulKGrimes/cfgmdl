#!/usr/bin/env python
""" Tools to manage Properties attached to client classes
"""

import time

from collections import OrderedDict as odict


from .utils import cast_type, Meta, Defs, defaults_decorator, defaults_docstring

try:
    basestring
except NameError:
    basestring = str



class Property(Defs):
    """Base class to attach managed attribute to class.

    Notes
    -----
    This is a "validator" class:  https://docs.python.org/3/howto/descriptor.html#validator-class

    It manages a Property for a client class using the __set_name__, __set__, __get__, and __delete__ functions.

    In the example above, for an object my_obj of client class MyClass
    the property val_float would store a hidden attribute my_obj._val_float

    my_obj.val_float uses Property.__get__() to access my_obj._val_float
    my_obj.val_float = 3.3 uses Property.__set__() to set my_obj._val_float (and validate the input value)
    del my_obj.val_float uses Property.__delete__() to set my_obj._val_float the default value
    """
    __metaclass__ = Meta

    defaults = odict([
        ('help', ("", 'Help description')),
        ('format', ('%s', 'Format string for printing')),
        ('dtype', (None, 'Data type')),
        ('default', (None, 'Default value')),
        ('required', (False, 'Is this propery required?')),
        ('unit', (None, 'Units for unit')),
    ])

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.help = None
        self.format = None
        self.dtype = type(None)
        self.default = None
        self.required = None
        self.unit = None
        self.public_name = None
        self.private_name = None
        self.time_name = None
        super(Property, self).__init__()
        self._load(**kwargs)

    def __set_name__(self, owner, name):
        """Set the name of the privately managed value"""
        self.public_name = name
        self.private_name = '_' + name
        self.time_name = '_' + name + '_timestamp'

    def __set__(self, obj, value):
        """Set the value in the client object

        Parameter
        ---------
        obj : ...
            The client object
        value : ...
            The value being seti
        This will use the `cast_type(self.dtype, value)` method to cast the requested value to the correct type.

        Rasies
        ------
        TypeError : The input value is the wrong type (i.e., not castable to self.dtype)

        ValueError : The input value failes validation for a Property sub-class (e.g., not a valid choice, or outside bounds)
        """
        try:
            cast_value = self._cast_type(value)
            self.validate_value(obj, cast_value)
        except (TypeError, ValueError) as msg:
            setattr(obj, self.private_name, None)
            setattr(obj, self.time_name, time.time())
            raise TypeError("Failed to set %s %s" % (self.private_name, msg)) from msg
        setattr(obj, self.private_name, cast_value)
        setattr(obj, self.time_name, time.time())

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
        attr = getattr(obj, self.private_name)
        if self.unit is None:
            return attr
        return self.unit(attr) #pylint: disable=not-callable

    def __delete__(self, obj):
        """Set the value to the default value

        This can be useful for sub-classes that use None
        to indicate an un-initialized value.
        """
        setattr(obj, self.private_name, self.default)
        setattr(obj, self.time_name, time.time())

    def _load(self, **kwargs):
        """Load kwargs key,value pairs into __dict__
        """
        defaults = {}
        # Require kwargs are in defaults
        for k in kwargs:
            if k not in self.defaults:
                msg = "Unrecognized attribute of %s: %s" % (self.__class__.__name__, k)
                raise AttributeError(msg)

        defaults.update(kwargs)

        # This doesn't overwrite the properties
        self.__dict__.update(defaults)

        # Make sure the default is valid
        _ = self._cast_type(self.default)


    def _cast_type(self, value):
        """Hook took override type casting"""
        return cast_type(self.dtype, value)

    @classmethod
    def defaults_docstring(cls, header=None, indent=None, footer=None):
        """Add the default values to the class docstring"""
        return defaults_docstring(cls.defaults, header=header, indent=indent, footer=footer) #pragma: no cover

    def validate_value(self, obj, value): #pylint: disable=unused-argument,no-self-use
        """Validate a value"""
        return

    def todict(self, obj):
        """Extract value """
        val = getattr(obj, self.private_name)
        if hasattr(val, 'todict'):
            return val.todict()
        return val
