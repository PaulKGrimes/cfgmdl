"""Tools to build classes"""

from collections import OrderedDict as odict

from .utils import expand_dict
from .property import Property

def build_sub_configurables(config_dict, type_dict):
    """ Build a set of of Property objects to manage a set of Configurables,

    Parameters
    ----------
    config_dict : `dict`
        Dictionary used to build the sub-objects

    type_dict : `dict`
        Dictionary mapping names to Configurable Class names

    Returns
    -------
    o_dict : `dict`
        odict(name:Property), i.e., a dictionary mapping names to the Property object to manage the owned objects

    Notes
    -----
    This function is used by build_class to extend classes algorithmically by attaching Property objects that will be used to
    access the data members of the class.
    """

    return odict([(key, Property(dtype=type_dict[val.pop('obj_type', None)])) for key, val in config_dict.items()])


def build_class(name, base_classes, config_dicts, type_dicts, **kwargs):
    """ Build a new class algorithmically.

    Parameters
    ----------
    name : `str`
        The name of the new class

    base_classes : `Iterable`
        The base classes

    config_dicts : `Iterable`
        Dictionaries used to build the sub-objects

    type_dicts : `Iterable`
        Dictionaries mapping names to Configurable Class names for each of the config_dicts


    Returns
    -------
    object : `Configurable`
        Newly-made object of the newly made type.
        The kwargs are based directly to the constructor of the new class, and the resulting object is returned.

    Notes
    -----
    This function is used to extend classes `Configurable` sub-classes algorithmically.

    If a `Configurable` object has some optional data members, this class will build them based
    on the config_dict.
    """
    kwcopy = kwargs.copy()

    props = odict()
    for config_dict_, type_dict_ in zip(config_dicts, type_dicts):
        use_dict_ = expand_dict(config_dict_)
        kwcopy.update(use_dict_)
        props.update(build_sub_configurables(use_dict_, type_dict_))

    new_class = type(name, base_classes, props)
    return new_class(**kwcopy)
