#!/usr/bin/env python
""" Tools to manage Property objects that consist of a set of allowed choics
"""

from copy import deepcopy

from .property import Property, defaults_decorator


class Choice(Property):
    """Property sub-class for defining a numerical Parameter.

    This includes value, bounds, error estimates and fixed/free status
    (i.e., for fitting)

    """

    # Better to keep the structure consistent with Property
    defaults = deepcopy(Property.defaults)
    defaults['choices'] = ([], 'Allowed values')

    # Overwrite the default dtype
    defaults['dtype'] = (str, 'Data type')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        super(Choice, self).__init__(**kwargs)

    def validate_value(self, obj, value):
        """Validate a value

        In this case it checks that value is in the set of allowed choices
        """
        if value is None:
            return
        if value not in self.choices: #pylint: disable=no-member
            raise ValueError("%s not allow, options are %s" % (value, self.choices))  #pylint: disable=no-member
