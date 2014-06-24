"""This module provides the rule parser.

The function :function:`parse_rule` parse and check each items of a raw rule.
A raw rule is a rule where items value may be string representation of other python types.
When the function returns, the raw rule is converted into a rule where all the values that have non string types associated have been converted to the relevant type.
"""

import string

from pyparsing import QuotedString, ParseException

from .range import parse_range, Range
from .rule_enforcer import check_value
from .exceptions import RuleError


# pattern to identify a condition expression
CONDEXP_KEY_PATTERN = QuotedString(quoteChar='{', endQuoteChar='}')

# rules for checking rule items
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


def parse_rule(rule):
    """Parse a raw rule.

    Parameters
    ----------
    rule : dict
        rule to parse

    Returns
    -------
    dict
        parsed rule
    list of str
        keys of the dependencies
    """
    parsed_rule = dict()

    items, ctx_rules = _split_sub_sections(rule)

    # parse the common rule items
    parsed_items = _parse_rule_items(items)
    parsed_rule.update(parsed_items)

    # parse contextual rules
    deps = list()
    for cond_exp, ctx_rule in ctx_rules.viewitems():
        deps += _parse_dependencies(cond_exp)

        # complete the context rule with inherited common rule
        completed_ctx_rule = dict(parsed_items)
        completed_ctx_rule.update(ctx_rule)

        parsed_ctx_rule = _parse_rule_items(completed_ctx_rule)
        parsed_rule[cond_exp] = parsed_ctx_rule
    return parsed_rule, deps


def _split_sub_sections(dict_):
    """Split simple items and sub-sections of a dictionary.

    Parameters
    ----------
    dict_ : dict
        dictionary to split

    Returns
    -------
    dict
        rule part with the common items
    dict of dict
        rule part with the contextual rules
    """
    items = dict()
    sub_sections = dict()
    for key, value in dict_.viewitems():
        if isinstance(value, dict):
            sub_sections[key] = value
        else:
            items[key] = value
    return items, sub_sections


def _parse_rule_items(rule):
    """Parse the non-conditional items of a rule.

    Parameters
    ----------
    rule : dict
        rule items to parse

    Returns
    -------
    dict
        rule converted to python types when possible.

    Raises
    ------
    RuleError
        if items are not keys of RULE_META_RULE
    """
    new_rule = dict()
    for key in ('exists', 'type'):
        new_rule[key] = check_value(rule.get(key),
                                    RULE_META_RULE[key]['exists'],
                                    RULE_META_RULE[key]['type'],
                                    allowed=RULE_META_RULE[key]['allowed'])

    if 'allowed' in rule:
        new_rule['allowed'] = _parse_allowed(rule['allowed'],
                                             new_rule['type'])

    if 'default' in rule:
        new_rule['default'] = check_value(rule['default'],
                                          True,
                                          new_rule['type'],
                                          allowed=new_rule.get('allowed'))

    # check there's no illegal keys
    if not set(rule).issubset(set(RULE_META_RULE)):
        msg = 'item with key "{}" is not a valid rule item'.format(key)
        raise RuleError(msg)

    return new_rule


def _parse_allowed(allowed, type_):
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
            allowed = parse_range(allowed)
        except ParseException:
            pass

    if isinstance(allowed, Range):
        # already a range
        if allowed.type != type_:
            msg = 'range type is "{}" but it should be "{}"'.format(
                allowed.type, type_)
            raise TypeError(msg)
        return allowed

    elif isinstance(allowed, str):
        allowed = map(string.strip, allowed.split(','))

    # always process a list
    if not isinstance(allowed, list):
        allowed = [allowed]

    # check each value and return
    return [check_value(value, True, type_) for value in allowed]


def _parse_dependencies(string):
    """Determine the dependencies from a conditional expression.

    Parameters
    ----------
    string : str
        a conditional expression

    Returns
    -------
    list of keys
        keys of the dependencies

    Raises
    ------
    RuleError
        when there is no dependency found
    """
    parsed = CONDEXP_KEY_PATTERN.searchString(string).asList()
    if parsed:
        return list(t[0] for t in parsed)
    else:
        msg = 'no dependency found in section {}'.format(string)
        raise RuleError(msg)
