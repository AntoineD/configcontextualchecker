import unittest

from configcontextualchecker.rule import FlatRule
from configcontextualchecker.range import Range
from configcontextualchecker.exceptions import ItemError, RuleError


class TestRuleParser(unittest.TestCase):

    def assertRuleEqual(self, expected, rule):
        return self.assertEqual(rule.type, expected['type']) and \
               self.assertEqual(rule.exists, expected['exists']) and \
               self.assertEqual(rule.allowed, expected['allowed']) and \
               self.assertEqual(rule.default, expected['default'])

    def test_parse_allowed(self):
        # range representation case OK
        allowed = ']0,2['
        expected = Range(0, True, 2, True)
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # range case OK
        allowed = expected = Range(0, True, 2, True)
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # range representation case bad type
        allowed = ']0,2['
        with self.assertRaises(TypeError):
            FlatRule._parse_allowed(allowed, float)

        # range case bad type
        allowed = Range(0, True, 2, True)
        with self.assertRaises(TypeError):
            FlatRule._parse_allowed(allowed, float)

        # non list case non-string type
        allowed = 0
        expected = [0]
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # non list case string
        allowed = '0'
        expected = [0]
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case non-string type
        allowed = [0]
        expected = [0]
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case string
        allowed = ['0']
        expected = [0]
        result = FlatRule._parse_allowed(allowed, int)
        self.assertEqual(expected, result)

        # list case string type
        allowed = '0'
        expected = ['0']
        result = FlatRule._parse_allowed(allowed, str)
        self.assertEqual(expected, result)

        # list case string several items
        allowed = '0,1,2 , 3'
        expected = ['0', '1', '2', '3']
        result = FlatRule._parse_allowed(allowed, str)
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

        result = FlatRule(rule)
        self.assertRuleEqual(expected, result)

        # not allowed default
        rule = {
            'exists': 'True',
            'type': 'int',
            'allowed': '0',
            'default': '1',
        }
        with self.assertRaises(ValueError):
            FlatRule(rule)

        # missing item
        rule = {
            'exists': 'True',
        }
        with self.assertRaises(ItemError):
            FlatRule(rule)

        # illegal item
        rule = {
            'exists': True,
            'type': int,
            'foo': 'True',
        }
        with self.assertRaises(RuleError):
            FlatRule(rule)

    def test_exists(self):
        result = FlatRule._check_value(0, True, int)
        self.assertEqual(result, 0)

        with self.assertRaises(ItemError):
            FlatRule._check_value(0, False, int)

        with self.assertRaises(ItemError):
            FlatRule._check_value(None, True, int)

    def test_type_use_type(self):
        result = FlatRule._check_value('int', True, type)
        self.assertEqual(result, int)

        result = FlatRule._check_value(int, True, type)
        self.assertEqual(result, int)

        result = FlatRule._check_value(0, True, int)
        self.assertEqual(result, 0)

        result = FlatRule._check_value('0', True, str)
        self.assertEqual(result, '0')

        with self.assertRaises(TypeError):
            FlatRule._check_value(0, True, str)

    def test_default(self):
        # existing value
        result = FlatRule._check_value(0, True, int, default=1)
        self.assertEqual(result, 0)

        # non existing value
        result = FlatRule._check_value(None, True, int, default=1)
        self.assertEqual(result, 1)

    def test_allowed(self):
        # allowed value
        result = FlatRule._check_value(0, True, int, allowed=(0,))
        self.assertEqual(result, 0)

        # not allowed value
        with self.assertRaises(ValueError):
            FlatRule._check_value(1, True, int, allowed=(0,))

    def test_type_string(self):
        data = {
            '0': int,
            '0.': float,
            'a': str,
            'int': type,
            'float': type,
            'str': type,
            'True': bool,
            'False': bool,
        }

        for datum, expected in data.items():
            self.assertEqual(FlatRule._type_string(datum), expected)

    def test_string_to_type(self):
        result = FlatRule._check_value('0', True, int, allowed=(0,))
        self.assertEqual(result, 0)

        result = FlatRule._check_value('False', True, bool)
        self.assertEqual(result, False)

        result = FlatRule._check_value('float', True, type)
        self.assertEqual(result, float)
