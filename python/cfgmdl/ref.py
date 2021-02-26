""" Property sub-class refering to properties of other objects
"""
import time

from copy import deepcopy

from .property import Property, defaults_decorator

class Ref(Property):
    """Property sub-class refering to properties of other objects
    """
    defaults = deepcopy(Property.defaults)
    defaults.pop('unit')
    defaults.pop('dtype')
    defaults['owner'] = (None, 'Object that owns datum')
    defaults['attr'] = (None, 'Name of attribute in object that owns datum')

    @defaults_decorator(defaults)
    def __init__(self, **kwargs):
        self.owner = None
        self.attr = None
        self.owner_name = None
        self.attr = None
        super(Ref, self).__init__(**kwargs)

    def __set_name__(self, owner, name):
        """Set the name of the privately managed value"""
        super(Ref, self).__set_name__(owner, name)
        self.owner_name = '_' + name + '_owner'
        if self.attr is None:
            self.attr = self.public_name

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

        """
        owner = getattr(obj, self.owner_name)
        if owner is None:
            return None
        val = getattr(owner, self.attr)
        setattr(obj, self.private_name, val)
        setattr(obj, self.time_name, time.time())
        return val

    def __set__(self, obj, value):
        """Set the pointer to the referenced object

        Parameter
        ---------
        obj : ...
            The client object
        value : ...
            The referenced object
        """        
        setattr(obj, self.owner_name, value)
        _ = self.__get__(obj, self.public_name)
        setattr(obj, self.time_name, time.time())

    def __delete__(self, obj):
        """Set the value to the default value

        This can be useful for sub-classes that use None
        to indicate an un-initialized value.
        """
        owner = getattr(obj, self.owner_name)
        if owner is not None:
            delattr(owner, self.attr)
        super(Ref, self).__delete__(obj)
