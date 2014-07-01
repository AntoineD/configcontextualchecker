import unittest
from configcontextualchecker.conditional_parser import Parser, ParserError


class TestExpressionParser(unittest.TestCase):

    SECTION = {
        'a': 0,
        'b': 1,
        'c': 2,
        'w': 0.,
        'd': 'e',
        'z': 'x y',
        't': True,
        'f': False,
        'g': {'h': 0},
        }

    def setUp(self):
        self.parser = Parser(self.SECTION)
        # parser.set_buffer(self.SECTION)

    def checkEqual(self, data, expected):
        result = self.parser.parse_string(data)
        self.assertEqual(result, expected)

    def test_ContainRaises(self):
        test_data = {
            # no list
            '{a} in 0': ParserError,
            '{a} not in 0': ParserError,
            # bad type
            '{a} in (x, y)': TypeError,
            }

        for data, error in test_data.items():
            self.assertRaises(error, parser.parse_string, data)

    def test_Contain(self):
        test_data = {
            '{a} in (0, 1)': True,
            '{w} in (0., 1.)': True,
            '{a} in (1, 1)': False,
            '{a} not in (0, 1)': False,
            '{a} not in (1, 1)': True,
            '{d} in (x, y)': False,
            '{d} not in (x, e)': False,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)

    def test_ComparisonRaises(self):
        # bad type
        test_data = (
            '{a} < a',
            )

        for data in test_data:
            self.assertRaises(TypeError, parser.parse_string, data)

    def test_Comparison(self):
        test_data = (
            '{a} < 1',
            '{a} <= 1',
            '{a} > 1',
            '{a} >= 1',
            '{a} == 1',
            '{a} != 1',
            '{b} < 1',
            '{b} <= 1',
            '{b} > 1',
            '{b} >= 1',
            '{b} == 1',
            '{b} != 1',
            '1 < {a} < 1',
            '1 < {b} < 1',
            '{a} < {b} < {c}',
            )

        for data in test_data:
            expected = eval(data.format(**self.SECTION))
            self.checkEqual(data, expected)

        # strings has to be handled manually
        self.checkEqual('{d} == e', True)
        self.checkEqual('{z} == "x y"', True)

        # non existing item always make the condition false
        self.checkEqual('{z} == 1', False)

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
            expected = eval(data)
            self.checkEqual(data, expected)

        # testing with items
        test_data2 = list()
        for data in test_data:
            data.replace('True', '{t}')
            data.replace('False', '{f}')
            test_data2 += [data]

        for data in test_data2:
            expected = eval(data.format(**self.SECTION))
            self.checkEqual(data, expected)

    def test_compound(self):
        test_data = {
            '{a} in (0, 1) and {b} == 1': True,
            '({a} in (0, 1) or {b} > 1) and {c} != 2': False,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)

    def test_dict_path(self):
        test_data = {
            '{/g/h} == 0': True,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)
