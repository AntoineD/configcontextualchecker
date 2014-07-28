import unittest
import os

from configcontextualchecker.condexp_parser import Parser
from configcontextualchecker.exceptions import ParserSyntaxError


class ErrorChecking(object):
    """Mixin class for error checking of exceptions."""

    __show = os.environ.get('SHOW_EXCEPTION', False)

    def checkErrors(self, test_data):
        """Check raised error messages.

        Parameters
        ----------
        test_data : dict
            dictionary with test data and expected error message items.
        """
        for data, error_items in test_data.items():
            with self.assertRaises(ParserSyntaxError) as error:
                self.parser.parse(data)
            print error.exception
            if error_items is None:
                expected = ParserSyntaxError.MSG_EOS
            else:
                expected = ParserSyntaxError.MSG_PATTERN.format(*error_items)
            if self.__show:
                print error.exception
            self.assertEqual(str(error.exception), expected)


class TestExpressionParser(unittest.TestCase, ErrorChecking):

    CONFIG = {
        'a': 0,
        'b': 1,
        'c': 2,
        'w': 0.,
        'd': 'e',
        'z': 'x y',
        't': True,
        'f': False,
        'g': {'h': True},
        }

    def setUp(self):
        self.parser = Parser()
        self.parser.config = self.CONFIG

    def checkEqual(self, data, expected=None):
        """Check parsing result."""
        result = self.parser.parse(data)
        if expected is None:
            expected = eval(data.format(**self.CONFIG))
        self.assertEqual(result, expected)

    def test_ContainRaises(self):
        test_data = {
            '0 in (0': None,
            '0 in 0': (
                '0',
                '0 in 0',
                '-----^',
            ),
            '0 in 0)': (
                '0',
                '0 in 0)',
                '-----^-',
            ),
            '0 in ()': (
                ')',
                '0 in ()',
                '------^',
            ),
            '0 in (0)': (
                ')',
                '0 in (0)',
                '-------^',
            ),
            '0 in (0,)': (
                ')',
                '0 in (0,)',
                '--------^',
            ),
        }

        self.checkErrors(test_data)

    def test_Contain(self):
        test_data = (
            '1 in (1, 0)',
            '0. in (2., 1., 0.)',
            '0 in (1, 1)',
            '0 not in (2, 0, 1)',
            '0 not in (1, 2)',
            '"e" in ("x", "y")',
            '"e" not in ("x", "e")',
            )

        for data in test_data:
            self.checkEqual(data)

    def test_ComparisonRaises(self):
        test_data = {
            '0 < "a"': (
                'a',
                '0 < "a"',
                '----^--',
            )
        }

        self.checkErrors(test_data)

    def test_Comparison(self):
        test_data = (
            '0 <  0',
            '0 <= 0',
            '0 >  0',
            '0 >= 0',
            '0 == 0',
            '0 != 0',
            '0. <  0.',
            '0. <= 0.',
            '0. >  0.',
            '0. >= 0.',
            '0. == 0.',
            '0. != 0.',
            )

        for data in test_data:
            self.checkEqual(data)

        # strings does not work with eval
        self.checkEqual('"e" == "e"', True)
        self.checkEqual('"e" != "e"', False)

    def test_Condition(self):
        test_data = (
            'True',
            'False',
            'not True',
            'not False',
            'True and True',
            'True or True',
            'True and False',
            'True or False',
            'False and False',
            'False or False',
            'True and not False',
            'not not True',
            'not(True and False)',
            'False or not True and True',
            'False or not True or not True',
            'False or not (True and True)',
            'True or False or True',
            'True or False or True and False',
            '(True or False or True) and False',
            )

        for data in test_data:
            self.checkEqual(data)

        # testing with items
        test_data2 = list()
        for data in test_data:
            data.replace('True', '{t}')
            data.replace('False', '{f}')
            test_data2 += [data]

        for data in test_data2:
            self.checkEqual(data)

    def test_compound(self):
        test_data = (
            '{a} in (0, 1) and {b} == 1',
            '({a} in (0, 1) or {b} > 1) and {c} != 2',
            '{a} < {b} and {b} < {c}',
            )

        for data in test_data:
            self.checkEqual(data)

    def test_dict_path(self):
        # OK
        test_data = {
            '{/g/h}': True,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)

        # KO
        test_data = {
            '{/foo} == 0': (
                '==',
                '{/foo} == 0',
                '-------^---',
            )
        }

        self.checkErrors(test_data)
