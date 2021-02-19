"""Small module for unit converision"""

import numpy as np

class Unit:
    """
    Object for handling unit conversions

    """
    to_SI_dict = {}

    def __init__(self, unit=None):
        # Dictionary of SI unit conversions
        # Check that passed unit is available
        if unit is None:
            self._SI = 1.
            self._name = ''
            return
        if isinstance(unit, str):
            if unit not in self.to_SI_dict:
                raise KeyError("Passed unit '%s' not understood by Unit object" % (unit))
            self._SI = self.to_SI_dict[unit]
            self._name = unit
            return
        self._SI = float(unit)
        self._name = "a.u."

    @property
    def name(self):
        """Return the units name"""
        return self._name

    def __call__(self, val):
        """Convert value to SI unit """
        return np.array(val) * self._SI

    def inverse(self, val):
        """Convert value from SI unit """
        return np.array(val) / self._SI

    @classmethod
    def update(cls, a_dict):
        """Update the mapping of unit names"""
        cls.to_SI_dict.update(a_dict)
