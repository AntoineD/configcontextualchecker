import unittest

from configcontextualchecker.rule_enforcer import check_value, \
    ItemError, _type_string


class TestRuleEnforcer(unittest.TestCase):

    def test_exists(self):
        result = check_value(0, True, int)
        self.assertEqual(result, 0)

        with self.assertRaises(ItemError):
            check_value(0, False, int)

        with self.assertRaises(ItemError):
            check_value(None, True, int)

    def test_type_use_type(self):
        result = check_value('int', True, type)
        self.assertEqual(result, int)

        result = check_value(int, True, type)
        self.assertEqual(result, int)

        result = check_value(0, True, int)
        self.assertEqual(result, 0)

        result = check_value('0', True, str)
        self.assertEqual(result, '0')

        with self.assertRaises(TypeError):
            check_value(0, True, str)

    def test_default(self):
        # existing value
        result = check_value(0, True, int, default=1)
        self.assertEqual(result, 0)

        # non existing value
        result = check_value(None, True, int, default=1)
        self.assertEqual(result, 1)

    def test_allowed(self):
        # allowed value
        result = check_value(0, True, int, allowed=(0,))
        self.assertEqual(result, 0)

        # not allowed value
        with self.assertRaises(ValueError):
            check_value(1, True, int, allowed=(0,))

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
            self.assertEqual(_type_string(datum), expected)

    def test_string_to_type(self):
        result = check_value('0', True, int, allowed=(0,))
        self.assertEqual(result, 0)

        result = check_value('False', True, bool)
        self.assertEqual(result, False)

        result = check_value('float', True, type)
        self.assertEqual(result, float)
