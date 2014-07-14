import unittest
from configcontextualchecker.conditional_parser import Parser


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
        'g': {'h': True},
        }

    def setUp(self):
        self.parser = Parser(self.SECTION)

    def checkEqual(self, data, expected):
        result = self.parser.parse_string(data)
        self.assertEqual(result, expected)

    def test_ContainRaises(self):
        test_data = {
            # no valid list
            '0 in 0': None,
            '0 in (0': None,
            '0 in 0)': None,
            '0 in ()': None,
            '0 in (0)': None,
            '0 in (0,)': None,
            # bad type
            '0 in (0., 1.)': TypeError,
            }

        for data, error in test_data.items():
            try:
                self.parser.parse_string(data)
            except Exception as e:
                print e
            # self.assertRaises(error, parser.parse_string, data)

    def test_Contain(self):
        test_data = {
            '1 in (1, 0)': True,
            '0. in (2., 1., 0.)': True,
            '{a} in (1, 1)': False,
            '{a} not in (0, 1)': False,
            '{a} not in (1, 2)': True,
            '{d} in ("x", "y")': False,
            '{d} not in ("x", "e")': False,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)

    def test_ComparisonRaises(self):
        # bad type
        test_data = (
            '{a} < "a"',
            )

        for data in test_data:
            self.assertRaises(TypeError, self.parser.parse_string, data)

    def test_Comparison(self):
        test_data = (
            '{a} <  1',
            '{a} <= 1',
            '{a} >  1',
            '{a} >= 1',
            '{a} == 1',
            '{a} != 1',
            '{w} <  0.',
            '{w} <= 0.',
            '{w} >  0.',
            '{w} >= 0.',
            '{w} == 0.',
            '{w} != 0.',
            '1 < {a} and {a} < 1',
            '1 < {b} and {b} < 1',
            '{a} < {b} and {b} < {c}',
            )

        for data in test_data:
            expected = eval(data.format(**self.SECTION))
            self.checkEqual(data, expected)

        # strings does not work with eval
        self.checkEqual('{d} == "e"', True)
        self.checkEqual('{d} != "e"', False)

        # non existing item always make the condition false
        # self.checkEqual('{z} == 1', False)

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
            '{/g/h}': True,
            }

        for data, expected in test_data.items():
            self.checkEqual(data, expected)
