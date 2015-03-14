"""This module provides the :class:`ConfigContextualChecker` class."""

import networkx

from .dict_path import set_from_path
from .rule_parser import parse_rule
from .rule_applier import apply_rule


class GraphNode(object):
    """Graph node class.

    Attributes
    ----------
    name: str
        node name
    rule: dict
        node rule
    dependencies: list of str
        keys of the dependencies

    Parameters
    ----------
    name: str
        node name
    rule: dict
        node rule
    dependencies: list of str
        keys of the dependencies
    """

    def __init__(self, name, rule, dependencies):
        self.name = name
        self.rule = rule
        self.dependencies = dependencies


class ConfigContextualChecker(object):
    """Config checker class.

    A :class:`ConfigContextualChecker` object is a callable that can process a
    config object.

    Parameters
    ----------
    rules_desc : dict
        rules descriptions

    Attributes
    ----------
    graph : networkx.DiGraph
        rules dependency graph
    """

    def __init__(self, rules_desc):
        # convert the rules descriptions into graph nodes
        nodes = list()
        for name, raw_rule in rules_desc.items():
            rule, deps = parse_rule(raw_rule)
            nodes += [GraphNode(name, rule, deps)]

        # create the dependency graph of the rules nodes
        self.graph = networkx.DiGraph()
        self.graph.add_nodes_from(nodes)
        name_node = dict()
        for node in nodes:
            name_node[node.name] = node
        for node in nodes:
            for dep in node.dependencies:
                self.graph.add_edge(name_node[dep], node)

    def __call__(self, config):
        """Check a config against the rules.

        Parameters
        ----------
        config : dict
            config to check
        """
        # loop over the rules nodes sorted according their dependencies
        for node in networkx.topological_sort(self.graph):
            value = apply_rule(node.name, node.rule, config)
            if value is not None:
                set_from_path(config, node.name, value)
