"""This module defines the functions to get and set a dictionary value
from a path.
"""

PATH_SEP = '/'


def get_from_path(dict_, path):
    """Get a dict value from a path.

    Parameters
    ----------
    dict_ : dict
        a dictionary
    path : str
        path to a key (included) or just a key
    value : any object
        value to be assigned

    Returns
    -------
    int or float or str
        value bound to the path
    """
    if path.startswith(PATH_SEP):
        path = path[1:]
        d = dict_
        v = None
        for p in path.split(PATH_SEP):
            try:
                v = d[p]
            except (TypeError, KeyError):
                # not a dict
                return None
            else:
                d = v
        return v
    else:
        return dict_.get(path)


def set_from_path(dict_, path, value):
    """Set a dict value from a path.

    Missing sections are created recursively, even if an existing value has to
    be overwritten.

    Parameters
    ----------
    dict_ : dict
        a dictionary
    path : str
        path to a key (included) or just a key
    value : any object
        value to be assigned
    """
    if path.startswith(PATH_SEP):
        d = dict_
        path_items = path.split(PATH_SEP)[1:]
        for p in path_items[:-1]:
            if isinstance(d.get(p), dict):
                d = d[p]
            else:
                d[p] = dict()
                d = d[p]
        d[path_items[-1]] = value
    else:
        dict_[path] = value
