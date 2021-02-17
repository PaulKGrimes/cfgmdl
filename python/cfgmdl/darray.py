"""Extend numpy.ndarray to behave like a fit parameter"""

from collections import OrderedDict as odict

import numpy as np


class Darray(np.ndarray):
    """Extend numpy.ndarray to be more useful as a set of fit parameters

    This carreis along bounds, errors, scale and flags showing if it if fixed or free
    """
    defaults = odict([('bounds', None),
                      ('errors', None),
                      ('free', False),
                      ('scale', None)])


    def __new__(cls, value, **kwds):
        """

        Notes
        -----

        This will create the ndarray instance of our type,
        from `value` and add on the additional attributes
        for this type

        It also triggers a call to Darray.__array_finalize__
        """
        obj = np.asarray(value).view(cls)
        # Finally, we must return the newly created object:
        for key, val in cls.defaults.items():
            kwval = kwds.pop(key, val)
            if kwval is not None:
                kwval = np.asarray(kwval)
            setattr(obj, '_%s' % key, kwval)
        return obj

    def __array_finalize__(self, obj):
        """ Set the additional attributes of the object

        Notes
        -----

        ``self`` is a new object resulting from
        ndarray.__new__(InfoArray, ...), therefore it only has
        attributes that the ndarray.__new__ constructor gave it -
        i.e. those of a standard ndarray.

        # We could have got to the ndarray.__new__ call in 3 ways:
        From an explicit constructor - e.g. DArray():
            obj is None
            (we're in the middle of the Darray.__new__
            constructor, and self.info will be set when we return to
            InfoArray.__new__)

        From view casting - e.g arr.view(Darray):
            obj is arr
            (type(obj) can be Darray)

        From new-from-template - e.g infoarr[:3]
            type(obj) is drray

        Note that it is here, rather than in the __new__ method,
        that we set the default value for 'bounds', etc..., because this
        method sees all creation of default objects - with the
        Darray.__new__ constructor, but also with
        arr.view(Darray).
        """
        if obj is None:
            return

        for key, val in self.defaults.items():
            attrval = getattr(obj, '_%s' % key, val)
            if attrval is not None:
                attrval = np.asarray(attrval)
            setattr(self, '_%s' % key, attrval)

    def __repr__(self):
        """Representation of this object"""
        ret = super(Darray, self).__repr__()
        if self.errors is None:
            ret += ' +- [None, None]'
        else:
            ret += ' +- [%s, %s]' % (self.errors[0], self.errors[1])

        if self.bounds is None:
            ret += ' [None, None]'
        else:
            ret += ' [%s, %s]' % (self.bounds[0], self.bounds[1])
        ret += " %s" % self.free
        return ret

    @property
    def errors(self):
        """Return the parameter errors"""
        return self._errors #pylint: disable=no-member

    @property
    def bounds(self):
        """Return the parameter bounds"""
        return self._bounds #pylint: disable=no-member

    @property
    def free(self):
        """Return the parameter fixed/free state"""
        return self._free #pylint: disable=no-member

    @property
    def symmetric_error(self):
        """Return the symmertic error

        Similar to above, but zero implies no error estimate,
        and otherwise this will either be the symmetric error,
        or the average of the low,high asymmetric errors.
        """
        # ADW: Should this be `np.nan`?
        if self.errors is None:
            return np.nan
        if np.isscalar(self.errors):
            return self.errors
        return 0.5 * (self.errors[0] + self.errors[1])

    def check_bounds(self, value):
        """Bounds checking"""
        if self.bounds is None:
            return
        if np.any(value < self.bounds[0]) or np.any(value > self.bounds[1]):
            msg = "Value outside bounds: %.2g [%.2g,%.2g]" % (value, self.bounds[0], self.bounds[1])
            raise ValueError(msg)
