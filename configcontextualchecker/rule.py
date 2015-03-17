"""This module provides the rule class.

A rule has a name, it is composed of a base :class:`FlatRule` and of contextual
rules.
The name is the path of the item that shall satisfy the rule.
A contextual rule is a :class:`FlatRule` bound to a conditional expression.
A conditional expression is an expression that has a truth value which may
depend on zero or more of the items in the config object to be checked.
In a conditional expression, the items of the config object are referred to by
their path within curly braces {}.
"""

import re

from .exceptions import RuleError
from .flat_rule import FlatRule
from . import condexp_parser


class Rule(object):
    """Rule class.

    Parameters
    ----------
    name : str
        name of the rule and path to the item in the config to be checked
    rule_def : dict
        rule definition

    Attributes
    ----------
    name : str
        name of the rule and path to the item in the config to be checked
    base_rule : :class:`FlatRule`
        flat rule that do not depend on conditional expressions
    dependencies : list of str
        names of the rules that the current rule depends on
    ctx_rules : dict of FlatRule
        contextual flat rules
    """

    # pattern to identify a condition expression
    RULE_NAME_PARSER = re.compile(r'(?:{(.+?)})')

    # conditional expression parser
    CONDEXP_PARSER = condexp_parser.Parser()

    def __init__(self, name, rule_def):
        self.name = name
        self.base_rule = FlatRule(rule_def)
        self.dependencies = list()
        self.ctx_rules = dict()
        self._parse(rule_def)

    def apply(self, config):
        """Check the item of a config dictionary.

        Parameters
        ----------
        config : dict
            config that contains the item

        Returns
        -------
        int or float or str or None
            item's value eventually converted to satisfy the rule
            or None if the item does not exist
        """
        # pass the config to the conditional expression parser about
        self.CONDEXP_PARSER.config = config

        # determine the rule to use
        for cond_exp, ctx_rule in self.ctx_rules.items():
            if self.CONDEXP_PARSER.parse(cond_exp):
                return ctx_rule.apply(self.name, config)
        else:
            return self.base_rule.apply(self.name, config)

    def _parse(self, rule_def):
        # parse the contextual rules, they override the root flat items,
        # also discover the dependencies
        for cond_exp, ctx_rule in rule_def.items():
            if not isinstance(ctx_rule, dict):
                continue
            self.dependencies += self._parse_dependencies(cond_exp)
            self.ctx_rules[cond_exp] = FlatRule(ctx_rule, self.base_rule)

        if self.name in self.dependencies:
            raise RuleError('a rule cannot depend on itself')

    @classmethod
    def _parse_dependencies(cls, cond_exp):
        """Determine the dependencies from a conditional expression.

        Parameters
        ----------
        cond_exp : str
            a conditional expression

        Returns
        -------
        list of str
            names of the rules the current rule depends on

        Raises
        ------
        RuleError
            when there is no dependency found
        """
        parsed = cls.RULE_NAME_PARSER.findall(cond_exp)
        if parsed:
            return parsed
        else:
            msg = 'no dependency found in section {0}'.format(cond_exp)
            raise RuleError(msg)
