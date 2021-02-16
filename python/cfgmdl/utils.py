#!/usr/bin/env python
"""
A few simple utilities to help parse configurations
"""

import numpy as np


try:
    basestring
except NameError:
    basestring = str


def defaults_docstring(defaults, header=None, indent=None, footer=None):
    """Return a docstring from a list of defaults.
    """
    if indent is None:
        indent = ''
    if header is None:
        header = ''
    if footer is None:
        footer = ''

    #width = 60
    #hbar = indent + width * '=' + '\n'  # horizontal bar
    hbar = '\n'

    s = hbar + (header) + hbar
    for key, value, desc in defaults:
        if isinstance(value, basestring):
            value = "'" + value + "'"
        if hasattr(value, '__call__'):
            value = "<" + value.__name__ + ">"

        s += indent +'%-12s\n' % ("%s :" % key)
        s += indent + indent + (indent + 23 * ' ').join(desc.split('\n'))
        s += ' [%s]\n\n' % str(value)
    s += hbar
    s += footer
    return s

def defaults_decorator(defaults):
    """Decorator to append default kwargs to a function.
    """
    def decorator(func):
        """Function that appends default kwargs to a function.
        """
        kwargs = dict(header='Keyword arguments\n-----------------\n',
                      indent='  ',
                      footer='\n')
        doc = defaults_docstring(defaults, **kwargs)
        if func.__doc__ is None:
            func.__doc__ = ''
        func.__doc__ += doc
        return func

    return decorator


def model_docstring(cls, header=None, indent=None, footer=None):
    """Return a docstring from a list of defaults.
    """
    if indent is None:
        indent = ''
    if header is None:
        header = ''
    if footer is None:
        footer = ''

    #width = 60
    #hbar = indent + width * '=' + '\n'  # horizontal bar
    hbar = '\n'

    props, _ = cls.find_properties()

    s = hbar + (header) + hbar
    for key, val in props.items():
        s += indent +'%-12s\n' % ("%s :" % key)
        s += indent + indent + (indent + 23 * ' ').join(val.help.split('\n'))
        s += ' [%s]\n\n' % str(val.default)
    s += hbar
    s += footer
    return s


class Meta(type): #pragma: no cover
    """Meta class for appending docstring with defaults
    """
    def __new__(mcs, name, bases, attrs):
        attrs['_doc'] = attrs.get('__doc__', '')
        return super(Meta, mcs).__new__(mcs, name, bases, attrs)

    @property
    def __doc__(cls):
        kwargs = dict(header='Parameters\n----------\n',
                      indent='  ',
                      footer='\n')
        return cls._doc + cls.defaults_docstring(**kwargs)


def is_none(val):
    """Check for values equivalent to None

    This will return True if val is one of None, 'none', 'None', np.nan
    """
    if not isinstance(val, (type(None), str)):
        return False
    return val in [None, 'none', 'None', np.nan]

def is_not_none(val):
    """Check for values equivalent to None

    This will return True if val is not on of  None, 'none', 'None', np.nan
    """
    if not isinstance(val, (type(None), str)):
        return True
    return val not in [None, 'none', 'None', np.nan]


def cast_type(dtype, value): #pylint: disable=too-many-return-statements
    """Casts an input value to a particular type

    Parameters
    ----------
    dtype : type
        The type we are casting to
    value : ...
        The value being cast

    Returns
    -------
    out : ...
        The object cast to dtype

    Raises
    ------
    TypeError if neither value nor dtype are None and the casting fails

    Notes
    -----
    This will proceed in the following order
        1.  If dtype is None it will simply return value
        2.  If value is None, 'None', or 'none' it will return None
        3.  If value is an instance of dtype it will return value
        4.  It will try to pass value to the constructor of dtype, i.e., return dtype(value)
        5.  It will try to use value as a list of argument to the constructor of dtype, i.e., return dtype(*value)
        6.  It will try to use value as a keyword dictionary to the constructor of dtype, i.e., return dtype(**value)
        7.  It will try to extract value['value'] and pass that to the constructor of dtype, i.e., return dtype(value['value'])
    """
    if is_none(dtype):
        return value
    # value = None is always allowed
    if is_none(value):
        return None
    # if value is an instance of self.dtype, then return it
    if isinstance(value, dtype):
        return value
    # try and cast value itself to dtype constructor
    try:
        return dtype(value)
    except (TypeError, ValueError):
        pass
    # try and cast the value as a list to dtype constructor
    try:
        return dtype(*value)
    except (TypeError, ValueError):
        pass
    # try and cast the value as a dict to dtype constructor
    try:
        return dtype(**value)
    except (TypeError, ValueError):
        pass
    # try and cast extract the 'value' item from a dict
    try:
        return dtype(value['value'])
    except (TypeError, ValueError, KeyError):
        pass
    msg = "Value of type %s, when %s was expected." % (type(value), dtype)
    raise TypeError(msg)
