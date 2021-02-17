#!/usr/bin/env python
""" Tools to manage Property objects that are derived from other Property objects manages by the same client class.
"""

from copy import deepcopy

from .property import Property, defaults_decorator


class Derived(Property):
    """Property sub-class for derived configuration Properties (i.e., Properties
    that depend on other Properties)

    This allows specifying the specifying a 'loader' function by name
    that is used to compute the value of the property.
    """
    defaults = deepcopy(Property.defaults) + [
        ('loader', None, 'Function to load datum')
    ]

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
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
        if val is not None:
            return val

        try:
            loader = self.loader  #pylint: disable=no-member
        except KeyError as err: #pragma: no cover
            raise AttributeError("Loader is not defined") from err

        # Try to run the loader.
        # Don't catch expections here, let the Model class figure it out
        val = loader()

        # Try to set the value
        try:
            setattr(obj, self.private_name, val)
        except TypeError as err:
            msg = "Loader must return variable of type %s or None, got %s" % (obj.__dict__['dtype'], type(val))
            raise TypeError(msg) from err

        return getattr(obj, self.private_name)
