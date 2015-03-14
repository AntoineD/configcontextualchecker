"""This module provides the :class:`ConfigContextualChecker` class.

This is the entry point into the checker.
"""

import networkx

from .dict_path import set_from_path
from .rule_parser import parse_rule
from .rule_applier import apply_rule


class RuleNode(object):
    """Represent a rule node in the rules with its dependent rules.

    Attributes
    ----------
    name: str
        node name
    rule: dict
        node rule
    dependencies: list of str
        node names the current node depends on

    Parameters
    ----------
    name: str
        node name
    rule: dict
        node rule
    dependencies: list of str
        node names the current node depends on
    """

    def __init__(self, name, rule, dependencies):
        self.name = name
        self.rule = rule
        self.dependencies = dependencies


class ConfigContextualChecker(object):
    """Contextual config checker class.

    A :class:`ConfigContextualChecker` object is a callable that can process a
    config object.

    Parameters
    ----------
    rules : dict
        rule definitions

    Attributes
    ----------
    graph : networkx.DiGraph
        rules dependency graph
    """

    def __init__(self, rules):
        # parse the rule definitions and convert them into rule nodes
        rule_nodes = list()
        for name, rule_def in rules.items():
            rule, deps = parse_rule(rule_def)
            rule_nodes += [RuleNode(name, rule, deps)]

        # create the dependency graph of the rule nodes
        self.graph = networkx.DiGraph()
        self.graph.add_nodes_from(rule_nodes)
        name_node = dict()
        for node in rule_nodes:
            name_node[node.name] = node
        for node in rule_nodes:
            for dep in node.dependencies:
                self.graph.add_edge(name_node[dep], node)

    def __call__(self, config):
        """Check a config against the rules.

        Parameters
        ----------
        config : dict
            config to check
        """
        # loop over the rule nodes sorted according to their dependencies and
        # apply the rules
        for node in networkx.topological_sort(self.graph):
            value = apply_rule(node.name, node.rule, config)
            if value is not None:
                set_from_path(config, node.name, value)
