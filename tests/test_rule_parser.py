import unittest

from configcontextualchecker.rule_parser import parse_rule, \
    _parse_dependencies, _split_flat_and_contextual_items, _parse_allowed,\
    _parse_flat_items
from configcontextualchecker.range import Range
from configcontextualchecker.exceptions import ItemError, RuleError


class TestRuleParser(unittest.TestCase):

    def test_parse_dependencies(self):
        # with deps
        expected = ['foo', 'baz']
        string = '{foo} bar {baz}'
        result = _parse_dependencies(string)
        self.assertEqual(expected, result)

        # w/o deps
        string = 'bar'
        expected = list()
        with self.assertRaises(RuleError):
            _parse_dependencies(string)

    def test_split_rule(self):
        rule = {
            'a': None,
            'b': dict(),
        }
        expected = ({'a': None}, {'b': dict()})
        result = _split_flat_and_contextual_items(rule)
        self.assertEqual(expected, result)

    def test_parse_allowed(self):
        # range representation case OK
        allowed = ']0,2['
        expected = Range(0, True, 2, True)
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # range case OK
        allowed = expected = Range(0, True, 2, True)
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # range reprentation case bad type
        allowed = ']0,2['
        with self.assertRaises(TypeError):
            _parse_allowed(allowed, float)

        # range case bad type
        allowed = Range(0, True, 2, True)
        with self.assertRaises(TypeError):
            _parse_allowed(allowed, float)

        # non list case non-string type
        allowed = 0
        expected = [0]
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # non list case string
        allowed = '0'
        expected = [0]
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case non-string type
        allowed = [0]
        expected = [0]
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case string
        allowed = ['0']
        expected = [0]
        result = _parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case string type
        allowed = '0'
        expected = ['0']
        result = _parse_allowed(allowed, str)
        self.assertEqual(expected, result)

        # list case string several items
        allowed = '0,1,2 , 3'
        expected = ['0', '1', '2', '3']
        result = _parse_allowed(allowed, str)
        self.assertEqual(expected, result)

    def test_parse_rule_items(self):
        # OK case
        rule = {
            'exists': 'True',
            'type': 'int',
            'allowed': '0',
            'default': '0',
        }
        expected = {
            'exists': True,
            'type': int,
            'allowed': [0],
            'default': 0,
        }

        result = _parse_flat_items(rule)
        self.assertEqual(expected, result)

        # not allowed default
        rule = {
            'exists': 'True',
            'type': 'int',
            'allowed': '0',
            'default': '1',
        }
        with self.assertRaises(ValueError):
            _parse_flat_items(rule)

        # missing item
        rule = {
            'exists': 'True',
        }
        with self.assertRaises(ItemError):
            _parse_flat_items(rule)

        # illegal item
        rule = {
            'exists': True,
            'type': int,
            'foo': 'True',
        }
        with self.assertRaises(RuleError):
            _parse_flat_items(rule)

    def test_parse_rule(self):
        # OK case
        rule = {
            'exists': True,
            'type': int,
            'allowed': 1,
            'default': 1,
            '{foo}': {
                'exists': 'False',
                'allowed': '1, 2',
            },
        }

        expected_rule = {
            'exists': True,
            'type': int,
            'allowed': [1],
            'default': 1,
            '{foo}': {
                'exists': False,
                'type': int,
                'allowed': [1, 2],
                'default': 1,
            },
        }

        expected_deps = ['foo']
        parsed_rule, deps = parse_rule(rule)
        self.assertEqual(expected_deps, deps)
        self.assertEqual(expected_rule, parsed_rule)

        # bad dependency
        rule = {
            'exists': True,
            'type': int,
            '': {},
        }

        with self.assertRaises(RuleError):
            parse_rule(rule)
