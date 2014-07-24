import unittest
import sys

from configcontextualchecker.range.range_parser import LowerBound, UpperBound
from configcontextualchecker.range import Range, RangeParser
from configcontextualchecker.exceptions import ParserSyntaxError


class TestRangeParser(unittest.TestCase):

    def setUp(self):
        self.parser = RangeParser()

    def test_Bound(self):
        data = {
            # lower open
            LowerBound(0, True): {
                -1: False,
                0: False,
                1: True,
            },
            # lower closed
            LowerBound(0, False): {
                -1: False,
                0: True,
                1: True,
            },
            # lower no bound
            LowerBound(None, True): {
                -1: True,
                0: True,
                1: True,
            },
            # upper open
            UpperBound(0, True): {
                -1: True,
                0: False,
                1: False,
            },
            # upper closed
            UpperBound(0, False): {
                -1: True,
                0: True,
                1: False,
            },
            # upper no bound
            UpperBound(None, False): {
                -1: True,
                0: True,
                1: True,
            },
        }

        for bound, test_data in data.items():
            for value, expected in test_data.items():
                self.assertEqual(expected, bound.check(value))

    def test_Range(self):
        data = {
            (0, True, 2, True): {
                -1: False,
                0: False,
                1: True,
                2: False,
                3: False,
            },
            (0, False, 2, True): {
                -1: False,
                0: True,
                1: True,
                2: False,
                3: False,
            },
            (0, True, 2, False): {
                -1: False,
                0: False,
                1: True,
                2: True,
                3: False,
            },
            (0, False, 2, False): {
                -1: False,
                0: True,
                1: True,
                2: True,
                3: False,
            },
            (0, False, None, False): {
                -1: False,
                0: True,
                sys.maxsize: True,
            },
            (None, False, 2, False): {
                -sys.maxsize: True,
                2: True,
                3: False,
            },
        }

        for args, test_data in data.items():
            range_ = Range(*args)
            for value, expected in test_data.items():
                if expected:
                    self.assertIn(value, range_)
                else:
                    self.assertNotIn(value, range_)

    def test_check_bound_values(self):
        # OK
        data = (
            (0, 1),
            (0., 1.),
            (0, None),
        )
        for bounds in data:
            Range._check_bounds_values(*bounds)

        # bad cases
        data = {
            (0, 1.): TypeError,
            (None, None): TypeError,
            (0, 0): ValueError,
            (1, 0): ValueError,
        }
        for bounds, error in data.items():
            with self.assertRaises(error):
                Range._check_bounds_values(*bounds)

    def test_type(self):
        data = {
            (0, 1): int,
            (None, 0.): float,
            (0, None): int,
        }
        for bounds, expected_type in data.items():
            type_ = Range(bounds[0], True, bounds[1], True).type
            self.assertEqual(expected_type, type_)

    def test_RangeParser(self):
        # OK
        data = {
            ']0,2[': (0, True, 2, True),
            '[0.,2.[': (0., False, 2., True),
            ']0,2]': (0, True, 2, False),
            '[0.,2.]': (0., False, 2., False),
            '[0,+inf]': (0, False, None, False),
            '[-inf,2.]': (None, False, 2, False),
        }

        for string, expected in data.items():
            args = self.parser._get_range_args(string)
            # test bound values type explicitely as for python 0 == 0.
            self.assertEqual(type(args[0]), type(expected[0]))
            self.assertEqual(expected, args)

        # KO
        with self.assertRaises(ParserSyntaxError):
            self.parser.parse_range('')
