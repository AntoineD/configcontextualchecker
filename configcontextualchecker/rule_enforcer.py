"""This module provides the ability to check a value against a rule."""

from .exceptions import ItemError
from . import condexp_parser
from .dict_path import get_from_path

CONDEXP_PARSER = condexp_parser.Parser()


def enforce_item_rule(item_path, rule, config):
    """Check a config's item against a rule.

    Parameters
    ----------
    item_path : str
        path pointing to a condif's item
    rule : dict
        rule that must be statisfied by the item
    config : dict
        config that contains the item

    Returns
    -------
    int or float or str or None
        items's value eventually converted to satisfy the rule's type
        or None if the item does not exist
    """
    CONDEXP_PARSER.config = config

    # determine the rule definition to use
    for cond_exp, ctx_rule in rule.items():
        # check for a contextual rule
        if not isinstance(ctx_rule, dict):
            continue

        if CONDEXP_PARSER.parse(cond_exp):
            use_rule = ctx_rule
            break
    else:
        # use common rule
        use_rule = rule

    value = get_from_path(config, item_path)
    return check_value(value,
                       use_rule['exists'],
                       use_rule['type'],
                       use_rule.get('allowed'),
                       use_rule.get('default'))


def check_value(value, exists, type_, allowed=None, default=None):
    """Check a value against a rule.

    Parameters
    ----------
    value : str representation or instance of type
        the value to be checked
    exists : bool
        whether the value exists or not
    type_ : type
        expected value type
    default : instance of type, optional
        value returned when item exists and value is None
    allowed : container object, optional
        value has to be in that container

    Returns
    -------
    type or int or float or str
        new value casted to type_ of from default

    Raises
    ------
    ItemError
        if the value when the value does not satisfy the rule
    """
    if exists:
        # check mandatory and default
        if value is None:
            if default is None:
                raise ItemError('item is mandatory')
            else:
                return default

        # check type
        if type(value) != type_ and _type_string(value) != type_:
            msg = 'bad item type: expected {0}, found {1}'.format(
                type_, _type_string(value))
            raise TypeError(msg)

        if isinstance(value, str):
            # convert the value to its represented type
            if type_ in (type, bool):
                # those types cannot be casted from a string so evaluate it
                value = eval(value)
            else:
                value = type_(value)

        # check allowed value
        if allowed is not None and value not in allowed:
            msg = 'value is not allowed: must be in {0}'.format(allowed)
            raise ValueError(msg)

        return value

    elif value is not None:
        raise ItemError('item is forbidden')


def _type_string(string):
    """Determine the type of a string representation.

    Supported types are type, int, float, str and bool.

    Parameters
    ----------
    string : str
        a string representation of a variable

    Returns
    -------
    type
        the type of the variable
    """
    try:
        if eval(string) in (int, float, str):
            return type
    except (ValueError, NameError):
        pass

    if string in ('True', 'False'):
        return bool

    try:
        int(string)
        return int
    except ValueError:
        pass

    try:
        float(string)
        return float
    except ValueError:
        pass

    return str
