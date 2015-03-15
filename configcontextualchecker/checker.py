"""This module provides the :class:`ConfigContextualChecker` class.

This is the entry point into the checker.
"""

import networkx

from .dict_path import set_from_path
from .rule import Rule


class ConfigContextualChecker(object):
    """Contextual config checker class.

    A :class:`ConfigContextualChecker` object is a callable that can process a
    config object or a dictionary.

    Parameters
    ----------
    rules_def : dict
        rule definitions

    Attributes
    ----------
    graph : :class:`networkx.DiGraph`
        rules dependency graph
    """

    def __init__(self, rules_def):
        self.graph = networkx.DiGraph()

        # parse the rule definitions
        rules = list()
        for name, rule_def in rules_def.items():
            rules += [Rule(name, rule_def)]

        # create the dependency graph of the rules
        self.graph.add_nodes_from(rules)

        name_node = dict()
        for rule in rules:
            name_node[rule.name] = rule

        for node in rules:
            for dep in node.dependencies:
                self.graph.add_edge(name_node[dep], node)

    def __call__(self, config):
        """Check a config against the rules.

        Parameters
        ----------
        config : dict
            config to check
        """
        # loop over the rules sorted according to their dependencies and
        # apply them
        for rule in networkx.topological_sort(self.graph):
            value = rule.apply(config)
            if value is not None:
                set_from_path(config, rule.name, value)
