import unittest

from configcontextualchecker.checker import ConfigContextualChecker
from configcontextualchecker.exceptions import ItemError


class TestConfigContextualChecker(unittest.TestCase):
    """Tests for ConfigContextualChecker."""

    def test_mandatory_item(self):
        rules = {
            'key-1': {
                'type': int,
                'exists': True,
            },
        }
        checker = ConfigContextualChecker(rules)

        # good
        buf = {'key-1': 1}
        checker(buf)

        # bad
        buf = dict()
        self.assertRaises(ItemError, checker, buf)

    def test_type(self):
        rules = {
            'key-1': {
                'type': int,
                'exists': True,
            },
        }
        checker = ConfigContextualChecker(rules)

        # OK
        buf = {'key-1': 1}
        checker(buf)

        # bad type
        buf = {'key-1': 'a'}
        self.assertRaises(TypeError, checker, buf)

    def test_exist(self):
        rules = {
            'key-1': {
                'type': int,
                'exists': False,
            },
        }
        checker = ConfigContextualChecker(rules)

        buf = {'key-1': 1}
        self.assertRaises(ItemError, checker, buf)

    def test_defaults(self):
        rules = {
            'key-1': {
                'type': int,
                'exists': True,
                'default': 1,
            },
        }
        checker = ConfigContextualChecker(rules)

        # buf overrides defaults
        buf = {'key-1': 2}
        ref = dict(buf)
        checker(buf)
        self.assertDictEqual(buf, ref)

        # default added
        buf = dict()
        ref = {'key-1': 1}
        checker(buf)
        self.assertDictEqual(buf, ref)

    def test_path(self):
        rules = {
            '/path/to/key-1': {
                'type': int,
                'exists': True,
                'default': 1,
            },
        }
        checker = ConfigContextualChecker(rules)

        buf = {'path': {'to': {'key-1': 1}}}
        checker(buf)
