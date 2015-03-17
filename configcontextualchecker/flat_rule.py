"""This module provides the flat rule class.
"""

from .range import RangeParser, Range
from .exceptions import RuleError, ItemError, ParserSyntaxError
from .dict_path import get_from_path


class FlatRule(object):
    """Flat rule class.

    A flat rule can check whether a value satisfy defined criteria.
    There are 4 criteria related to a value:
    * its type,
    * whether it shall exist or not,
    * its allowed values,
    * its default when its not defined.

    A value is defined if it's not None.

    Parameters
    ----------
    rule_def : dict
        rule definition
    other : Rule, optional
        other rule to copy undefined criteria from

    Attributes
    ----------
    type : int, float, str
        type of the item's value
    exists : bool
        existence of the item
    allowed : list, Range, None
        allowed values
    default : int, float, str, None
        default value of the item
    """

    # rules for checking a rule definition
    RULE_META_RULE = {
        'exists': {
            'exists': True,
            'type': bool,
            'allowed': (True, False),
        },
        'type': {
            'exists': True,
            'type': type,
            'allowed': (int, float, str),
        },
        'default': {
            # 'exists': default is optional
            # 'type': determined from rule's type
            # 'allowed': determined from rule's allowed
        },
        'allowed': {
            # 'exists': allowed is optional
            # 'type': determined from rule's type
        },
    }

    # value range parser
    RANGE_PARSER = RangeParser()

    def __init__(self, rule_def, other=None):
        # copy the rule definition as it may be modified
        rule_def_ = dict(rule_def)

        if other is None:
            self.type = None
            self.exists = None
            self.allowed = None
            self.default = None
        else:
            # copy other attributes into the rule definition when they are
            # missing
            for key in self.RULE_META_RULE:
                if key not in rule_def_:
                    rule_def_[key] = getattr(other, key)

        self._parse(rule_def_)

    def apply(self, item_path, config):
        """Check a config's item against a rule.

        Parameters
        ----------
        item_path : str
            path pointing to a config's item
        rule : dict
            rule that must be satisfied by the item
        config : dict
            config that contains the item

        Returns
        -------
        int or float or str or None
            item's value eventually converted to satisfy the rule's type
            or None if the item does not exist
        """
        current_value = get_from_path(config, item_path)
        return self._check_value(current_value,
                                 self.exists,
                                 self.type,
                                 self.allowed,
                                 self.default)

    def _parse(self, rule_def):
        # check possible items
        for key, value in rule_def.items():
            if isinstance(value, dict):
                continue
            if key not in self.RULE_META_RULE.keys():
                raise RuleError('illegal key {0}'.format(key))

        meta_rule = self.RULE_META_RULE['type']
        self.type = self._check_value(rule_def.get('type'),
                                      meta_rule['exists'],
                                      meta_rule['type'],
                                      meta_rule['allowed'])

        meta_rule = self.RULE_META_RULE['exists']
        self.exists = self._check_value(rule_def.get('exists'),
                                        meta_rule['exists'],
                                        meta_rule['type'],
                                        meta_rule['allowed'])

        if 'allowed' in rule_def:
            self.allowed = self._parse_allowed(rule_def['allowed'],
                                               self.type)

        if 'default' in rule_def:
            self.default = self._check_value(rule_def['default'],
                                             True,
                                             self.type,
                                             self.allowed)

    @classmethod
    def _parse_allowed(cls, allowed, type_):
        """Parse the allowed item of a rule.

        Parameters
        ----------
        allowed : str or list or range
            rule's allowed definition
        type_ : type
            rule's type

        Returns
        -------
        list of int or list of float or list of str or Range
            parsed allowed settings
        """
        if isinstance(allowed, str):
            # deal first with range representation so range type checking is
            # done once
            try:
                allowed = cls.RANGE_PARSER.parse(allowed)
            except ParserSyntaxError:
                pass

        if isinstance(allowed, Range):
            # already a range
            if allowed.type != type_:
                msg = 'range type is "{0}" but it should be "{1}"'.format(
                    allowed.type, type_)
                raise TypeError(msg)
            return allowed

        elif isinstance(allowed, str):
            allowed = [s.strip() for s in allowed.split(',')]

        # always process a list
        if not isinstance(allowed, list):
            allowed = [allowed]

        # check each value and return
        return [cls._check_value(value, True, type_) for value in allowed]

    @classmethod
    def _check_value(cls, value, exists, type_, allowed=None, default=None):
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
            if type(value) != type_ and cls._type_string(value) != type_:
                msg = 'bad item type: expected {0}, found {1}'.format(
                    type_, cls._type_string(value))
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

    @staticmethod
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
