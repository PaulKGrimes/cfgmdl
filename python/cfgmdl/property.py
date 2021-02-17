#!/usr/bin/env python
""" Tools to manage Properties attached to client classes
"""


from .utils import cast_type, Meta, defaults_decorator, defaults_docstring


try:
    basestring
except NameError:
    basestring = str



class Property:
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

    defaults = [
        ('help', "", 'Help description'),
        ('format', '%s', 'Format string for printing'),
        ('dtype', None, 'Data type'),
        ('default', None, 'Default value'),
        ('required', False, 'Is this propery required?'),
    ]

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self._load(**kwargs)
        self.private_name = None

    def __set_name__(self, owner, name):
        """Set the name of the privately managed value"""
        self.private_name = '_' + name

    def __set__(self, obj, value):
        """Set the value in the client object

        Parameter
        ---------
        obj : ...
            The client object
        value : ...
            The value being set

        This will use the `cast_type(self.dtype, value)` method to cast the requested value to the correct type.

        Rasies
        ------
        TypeError : The input value is the wrong type (i.e., not castable to self.dtype)

        ValueError : The input value failes validation for a Property sub-class (e.g., not a valid choice, or outside bounds)
        """
        try:
            cast_value = cast_type(self.dtype, value)  #pylint: disable=no-member
            self.validate_value(cast_value)
        except (TypeError, ValueError) as msg:
            setattr(obj, self.private_name, None)
            raise msg
        setattr(obj, self.private_name, cast_value)

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
        try:
            return getattr(obj, self.private_name)
        except AttributeError:
            setattr(obj, self.private_name, self.default)  #pylint: disable=no-member
        return getattr(obj, self.private_name)

    def __delete__(self, obj):
        """Set the value to the default value

        This can be useful for sub-classes that use None
        to indicate an un-initialized value.
        """
        setattr(obj, self.private_name, self.default)  #pylint: disable=no-member

    def _load(self, **kwargs):
        """Load kwargs key,value pairs into __dict__
        """
        defaults = {d[0]:d[1] for d in self.defaults}
        # Require kwargs are in defaults
        for k in kwargs:
            if k not in defaults:
                msg = "Unrecognized attribute of %s: %s" % (self.__class__.__name__, k)
                raise AttributeError(msg)
        defaults.update(kwargs)

        # This doesn't overwrite the properties
        self.__dict__.update(defaults)

        # Make sure the default is valid
        _ = cast_type(self.dtype, self.default)  #pylint: disable=no-member

    @classmethod
    def defaults_docstring(cls, header=None, indent=None, footer=None):
        """Add the default values to the class docstring"""
        return defaults_docstring(cls.defaults, header=header,
                                  indent=indent, footer=footer)

    def validate_value(self, value): #pylint: disable=unused-argument,no-self-use
        """Validate a value"""
        return
