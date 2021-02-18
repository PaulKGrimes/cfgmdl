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

from .property import Property
from .derived import Derived
from .parameter import Parameter

from .utils import Meta, model_docstring

class Model:
    """Base class for Configurable Models

    Examples::

        # A simple class with some managed Properties
        class MyClass(Model):

            val_float = Property(dtype=float, default=0.0, help="A float value")
            val_int = Property(dtype=int, default=1, help="An integer value")
            val_required = Property(dtype=float, required=True, help="A float value")
            val_str = Property(dtype=str, default="", help="A string value")
            val_list = Property(dtype=list, default=[], help="An list value")
            val_dict = Property(dtype=list, default={}, help="A dictionary value")

        # A class with nested configuration
        class MyPair(Model):
            val_first = Property(dtype=MyClass, required=True, help="First MyClass object")
            val_second = Property(dtype=MyClass, required=True, help="Second MyClass object")


        # Default, all Properties take their default values (must provide required Properties)
        my_obj = MyClass(val_required=3.)

        # Access Properties
        my_obj.val_float
        my_obj.val_str
        my_obj.val_list
        my_obj.val_dict
        my_obj.val_required

        # Set Properties
        my_obj.val_float = 5.4
        my_obj.val_int = 3
        my_obj.val_dict = dict(a=3, b=4)

        # This will fail with a TypeError
        my_obj.val_float = "not a float"

        # Override values in construction
        my_obj = MyClass(val_required=3., val_float=4.3, val_int=2, val_str="Hello World")

        # Build nested Configurables
        my_pair = MyPair(val_first=dict(val_required=3.), val_second=dict(val_required=4.))

        my_pair.val_first.val_float
        my_pair.val_second.val_int

    """

    __metaclass__ = Meta

    def __init__(self, **kwargs):
        """ C'tor.  Build from a set of keyword arguments.
        """
        self._properties, self._params = self.find_properties()
        self._init_properties(**kwargs)
        self._cache()

    @classmethod
    def find_properties(cls):
        """Find properties that belong to this model"""
        the_classes = cls.mro()
        props = odict()
        params = odict()
        for the_class in the_classes:
            for key, val in the_class.__dict__.items():
                if isinstance(val, Property):
                    props[key] = val
                if isinstance(val, Parameter):
                    params[key] = val
        return props, params

    def __str__(self, indent=0):
        """ Cast model as a formatted string
        """
        try:
            ret = '{0:>{2}}{1}'.format('', self.name, indent)
        except AttributeError:
            ret = "%s" % (type(self))
        if not self._properties: #pragma: no cover
            return ret
        ret += '\n{0:>{2}}{1}'.format('', 'Parameters:', indent + 2)
        width = len(max(self._properties.keys(), key=len))
        for name in self._properties.keys():
            value = getattr(self, name)
            par = '{0!s:{width}} : {1!r}'.format(name, value, width=width)
            ret += '\n{0:>{2}}{1}'.format('', par, indent + 4)
        return ret

    @classmethod
    def defaults_docstring(cls, header=None, indent=None, footer=None):
        """Add the default values to the class docstring"""
        return model_docstring(cls, header=header, indent=indent, footer=footer) #pragma: no cover

    def getp(self, name):
        """
        Get the named `Property`.

        Parameters
        ----------
        name : str
            The property name.

        Returns
        -------
        param : `Property`
            The parameter object.
        """
        return self._properties[name]

    def setp(self, name, **kwargs):
        """
        Set the value (and properties) of the named parameter.

        Parameters
        ----------
        name : str
            The parameter name.

        Keywords
        --------
        clear_derived : bool
            Flag to clear derived objects in this model

        Notes
        -----
        The other keywords are passed to the Property.__set__() function
        """
        kwcopy = kwargs.copy()
        if 'value' in kwcopy:
            value = kwcopy.pop('value')
            setattr(self, name, value)
        if kwcopy:
            print(kwcopy)
            setattr(self, name, kwcopy)
        self._cache(name)

    def set_attributes(self, **kwargs):
        """
        Set a group of attributes (parameters and members).  Calls
        `setp` directly, so kwargs can include more than just the
        parameter value (e.g., bounds, free, etc.).
        """
        kwargs = dict(kwargs)
        for name, value in kwargs.items():
            # Raise AttributeError if param not found
            try:
                self.getp(name)
            except KeyError as msg:
                raise KeyError("Warning: %s does not have attribute %s" %
                       (type(self), name)) from msg
            # Set attributes
            self.setp(name, value=value)

    def _init_properties(self, **kwargs):
        """ Loop through the list of Properties,
        extract the derived and required properties and do the
        appropriate book-keeping
        """
        missing = {}
        kwcopy = kwargs.copy()
        for k, p in self._properties.items():
            if k not in kwcopy and p.required:
                missing[k] = p
            pval = kwcopy.pop(k, p.default)
            p.__set__(self, pval)
            if isinstance(p, Derived):
                if p.loader is None:
                    p.loader = self.__getattribute__("_load_%s" % k)
                elif isinstance(p.loader, str):
                    p.loader = self.__getattribute__(p.loader)
                if not callable(p.loader):
                    raise ValueError("Callabe loader not defined for Derived object", type(self), k, p.loader)
        if missing:
            raise ValueError("One or more required properties are missing ", type(self), missing.keys())
        if kwcopy:
            raise KeyError("Warning: %s does not have attributes %s" % (type(self), kwcopy))

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

    def param_errors(self, pnames=None):
        """ Return an array with the parameter errors

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter errors

        Note that this is a N x 2 array.
        """
        l = self.get_params(pnames)
        v = [getattr(self, p.errors_name) for p in l]
        return np.array(v)

    def param_sym_errors(self, pnames=None):
        """ Return an array with the parameter errors

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter errors

        Note that this is a N x 2 array.
        """
        l = self.get_params(pnames)
        v = [p.symmetric_error(self) for p in l]
        return np.array(v)

    def param_bounds(self, pnames=None):
        """ Return an array with the parameter bounds

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter errors

        Note that this is a N x 2 array.
        """
        l = self.get_params(pnames)
        v = [getattr(self, p.bounds_name) for p in l]
        return np.array(v)

    def param_scales(self, pnames=None):
        """ Return an array with the parameter bounds

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter scale factors
        """
        l = self.get_params(pnames)
        v = [getattr(self, p.scale_name) for p in l]
        return np.array(v)

    def param_free(self, pnames=None):
        """ Return an array with the parameter bounds

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter free flags
        """
        l = self.get_params(pnames)
        v = [getattr(self, p.free_name) for p in l]
        return np.array(v)

    def param_tostr(self, pnames=None):
        """ Return an array with the parameter bounds

        Parameters
        ----------
        pname : list of string or none
           If a list of strings, get the Parameter objects with those names

           If none, get all the Parameter objects

        Returns
        -------
        ~numpy.array of parameter free flags
        """
        l = self.get_params(pnames)
        s = ""
        for p in l:
            s += p.public_name
            s += ": x"
            s += p.tostr(self)
            s += "\n"
        return s

    def todict(self):
        """ Return self cast as an '~collections.OrderedDict' object
        """
        return odict([(key, val.todict(self)) for key, val in self._properties.items()])

    def _cache(self, name=None):
        """
        Method called in `setp` to cache any computationally
        intensive properties after updating the parameters.

        Parameters
        ----------
        name : string
           The parameter name.

        Returns
        -------
        None
        """
        #pylint: disable=unused-argument, no-self-use
        return
