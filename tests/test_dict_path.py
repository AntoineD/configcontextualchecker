import unittest

from configcontextualchecker.dict_path import get_from_path, set_from_path


class TestDictPath(unittest.TestCase):

    def test_get_from_path(self):
        # no path
        path = 'a'
        dict_ = {'a': 0}
        expected = 0
        result = get_from_path(dict_, path)
        self.assertEqual(result, expected)

        # existing path
        path = '/a/b/c'
        dict_ = {'a': {'b': {'c': 0}}}
        expected = 0
        result = get_from_path(dict_, path)
        self.assertEqual(result, expected)

        # partially existing path
        path = '/a/b/c'
        dict_ = {'a': 0}
        expected = None
        result = get_from_path(dict_, path)
        self.assertEqual(result, expected)

        # non existing path
        path = '/a/b/c'
        dict_ = dict()
        expected = None
        result = get_from_path(dict_, path)
        self.assertEqual(result, expected)

    def test_set_from_path(self):
        # no path
        path = 'a'
        expected = {'a': 0}
        result = dict()
        set_from_path(result, path, 0)
        self.assertEqual(result, expected)

        # non existing path
        path = '/a/b/c'
        expected = {'a': {'b': {'c': 0}}}
        result = dict()
        set_from_path(result, path, 0)
        self.assertEqual(result, expected)

        # existing path
        path = '/a/b/c'
        expected = {'a': {'b': {'c': 0}}}
        result = {'a': {'b': {'c': 1}}}
        set_from_path(result, path, 0)
        self.assertEqual(result, expected)

        # partially existing path
        path = '/a/b/c'
        expected = {'a': {'b': {'c': 0}}}
        result = {'a': None}
        set_from_path(result, path, 0)
        self.assertEqual(result, expected)

        # partially existing path with other section
        path = '/a/b/c'
        expected = {'a': {'b': {'c': 0}, 'd': None}}
        result = {'a': {'d': None}}
        set_from_path(result, path, 0)
        self.assertEqual(result, expected)
