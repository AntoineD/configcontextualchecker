"""This module provides a parser for the rule definitions.

The function :function:`parse_rule` parse and check each items of a rule
definition.
A rule definition is a rule where items value may be string representation of
other python types.
When the function :function:`parse_rule` returns, the rule definition is
converted into a plain rule where all the values that have non string types
have been converted to the relevant type.

A rule is composed of flat items and contextual items.
Flat items do not depend on other rules, contextual rules do and are defined
with condition expressions.
A condition expression is an expression that has a truth value and depends on
other rules in the graph of rules.
Other rules are referred to by their names within curly braces {}.
"""

import re

from .range import RangeParser, Range
from .rule_applier import check_value
from .exceptions import RuleError, ParserSyntaxError


# pattern to identify a condition expression
RULE_NAME_PARSER = re.compile(r'(?:{(.+?)})')

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

# for parsing values ranges
RANGE_PARSER = RangeParser()


def parse_rule(rule_def):
    """Parse a rule definition.

    Parameters
    ----------
    rule : dict
        rule definition to parse

    Returns
    -------
    dict
        parsed rule
    list of str
        names of the rules the current rule depends on
    """
    rule = dict()

    # split apart the contextual items and the flat items
    flat_items_def, ctx_items_def = _split_flat_and_contextual_items(rule_def)

    # parse the flat items first as the contextual items are based on them
    flat_items = _parse_flat_items(flat_items_def)
    rule.update(flat_items)

    # parse the contextual items, their are composed of sub-rules that override
    # the root flat items, also discover the dependencies
    deps = list()
    for cond_exp, ctx_rule in ctx_items_def.items():
        deps += _parse_dependencies(cond_exp)

        # start off the contextual rule with the root flat items as a
        # contextual rule may only define the items that override the flat items
        completed_ctx_rule = dict(flat_items)
        completed_ctx_rule.update(ctx_rule)

        parsed_ctx_rule = _parse_flat_items(completed_ctx_rule)
        rule[cond_exp] = parsed_ctx_rule

    return rule, deps


def _split_flat_and_contextual_items(rule_def):
    """Split flat and contextual items of a rule.

    It returns to split simple items and sub-sections of a dictionary.

    Parameters
    ----------
    dict_ : dict
        dictionary to split

    Returns
    -------
    dict
        flat items
    dict of dict
        contextual items
    """
    items = dict()
    sub_sections = dict()
    for key, value in rule_def.items():
        if isinstance(value, dict):
            sub_sections[key] = value
        else:
            items[key] = value
    return items, sub_sections


def _parse_flat_items(rule_items):
    """Parse the flat items of a rule definition.

    Parameters
    ----------
    rule_def : dict
        rule items to parse

    Returns
    -------
    dict
        rule converted to python types when possible

    Raises
    ------
    RuleError
        if items have illegal keys
    """
    rule = dict()
    for key in ('exists', 'type'):
        rule[key] = check_value(rule_items.get(key),
                                RULE_META_RULE[key]['exists'],
                                RULE_META_RULE[key]['type'],
                                allowed=RULE_META_RULE[key]['allowed'])

    if 'allowed' in rule_items:
        rule['allowed'] = _parse_allowed(rule_items['allowed'],
                                         rule['type'])

    if 'default' in rule_items:
        rule['default'] = check_value(rule_items['default'],
                                      True,
                                      rule['type'],
                                      allowed=rule.get('allowed'))

    # check there's no illegal keys
    if not set(rule_items).issubset(set(RULE_META_RULE)):
        keys = set(rule_items) - set(RULE_META_RULE)
        msg = 'item with keys "{0}" is not a valid rule item'.format(keys)
        raise RuleError(msg)

    return rule


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
            allowed = RANGE_PARSER.parse(allowed)
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
    return [check_value(value, True, type_) for value in allowed]


def _parse_dependencies(condexp):
    """Determine the dependencies from a conditional expression.

    Parameters
    ----------
    condexp : str
        a conditional expression

    Returns
    -------
    list of keys
        names of the rules the current rule depends on

    Raises
    ------
    RuleError
        when there is no dependency found
    """
    parsed = RULE_NAME_PARSER.findall(condexp)
    if parsed:
        return parsed
    else:
        msg = 'no dependency found in section {0}'.format(condexp)
        raise RuleError(msg)
