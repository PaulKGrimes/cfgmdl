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
from collections.abc import Mapping

from .property import Property
from .derived import Derived

from .utils import Meta, model_docstring

class Configurable:
    """Base class for Configurable objects

    Examples::

        # A simple class with some managed Properties
        class MyClass(Configurable):

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
        self._properties = self.find_properties()
        self._init_properties(**kwargs)
        self._cache()

    @classmethod
    def find_properties(cls):
        """Find properties that belong to this model"""
        the_classes = cls.mro()
        props = odict()
        for the_class in the_classes:
            for key, val in the_class.__dict__.items():
                if isinstance(val, Property):
                    props[key] = val
        return props

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

    def update(self, *args, **kwargs):
        """
        Set a group of attributes (parameters and members).  Calls
        `setp` directly, so kwargs can include more than just the
        parameter value (e.g., bounds, free, etc.).
        """
        if args:
            raise ValueError("Argument passed to Model.upate() %s" % args)

        kwargs = dict(kwargs)
        for name, value in kwargs.items():
            # Raise KeyError if Property not found
            try:
                prop = self._properties[name]
            except KeyError as err:
                raise KeyError("Warning: %s does not have properties %s" % (type(self), name)) from err

            attr = getattr(self, '_%s' % name)
            if isinstance(attr, Configurable):
                # Set attributes
                if isinstance(value, Mapping):
                    attr.update(**value)
                else:
                    attr.update(value)
            else:
                prop.__set__(self, value)


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

    def todict(self):
        """ Return self cast as an '~collections.OrderedDict' object
        """
        return odict([(key, val.todict(self)) for key, val in self._properties.items()])


    def _cache(self, name=None):
        """
        Method called in  to cache any computationally
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
