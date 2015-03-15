import unittest

from configcontextualchecker.rule import Rule
from configcontextualchecker.exceptions import RuleError


class TestRuleParser(unittest.TestCase):

    def assertRuleEqual(self, expected, rule):
        self.assertEqual(rule.type, expected['type'])
        self.assertEqual(rule.exists, expected['exists'])
        self.assertEqual(rule.allowed, expected['allowed'])
        self.assertEqual(rule.default, expected['default'])

    def test_parse_dependencies(self):
        # with dependencies
        expected = ['foo', 'baz']
        string = '{foo} bar {baz}'
        result = Rule._parse_dependencies(string)
        self.assertEqual(expected, result)

        # self-dependence
        with self.assertRaises(RuleError):
            Rule.name = 'foo'
            Rule._parse_dependencies('foo')

        # w/o dependencies
        with self.assertRaises(RuleError):
            Rule._parse_dependencies('bar')

    def test_parse_rule(self):
        # OK case
        rule_def = {
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

        rule = Rule('', rule_def)

        self.assertEqual(['{foo}'], rule.ctx_rules.keys())
        self.assertRuleEqual(expected_rule, rule.base_rule)
        self.assertRuleEqual(expected_rule['{foo}'], rule.ctx_rules['{foo}'])

        # bad dependency
        rule_def = {
            'exists': True,
            'type': int,
            '': {},
        }

        with self.assertRaises(RuleError):
            Rule('', rule_def)
