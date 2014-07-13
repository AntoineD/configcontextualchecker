from ply import lex, yacc

from .dict_path import get_from_path


class ParserError(Exception):
    pass


class Parser(object):

    debug = 0

    tokens = (
        'BOOL',
        'INTEGER',
        'FLOAT',
        'ITEM',
        'NOT',
        'AND',
        'OR',
        'LPAREN',
        'RPAREN',
        'EQ',
        'NE',
        'LT',
        'GT',
        'LE',
        'GE',
        'STRING',
        'COMMA',
        'IN',
    )

    # Tokens
    t_NOT = r'not'
    t_AND = r'and'
    t_OR = r'or'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_EQ = r'=='
    t_NE = r'!='
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_COMMA = r','
    t_IN = r'in'

    t_ignore = " \t"

    @staticmethod
    def t_STRING(t):
        r'\"([^\\"]|(\\.))*\"'
        t.value = t.value.strip('"')
        return t

    @staticmethod
    def t_INTEGER(t):
        r'[+-]?\d+'
        t.value = eval(t.value)
        return t

    @staticmethod
    def t_FLOAT(t):
        r'\d+\.\d*([eE]\d+)?'
        t.value = eval(t.value)
        return t

    @staticmethod
    def t_BOOL(t):
        r'True|False'
        t.value = eval(t.value)
        return t

    def t_ITEM(self, t):
        r'{.+?}'
        type_token = {
            int: 'INTEGER',
            float: 'FLOAT',
            str: 'STRING',
            bool: 'BOOL',
        }
        # import pudb; pudb.set_trace()
        # TODO: check existence or error out
        t.value = get_from_path(self.config, t.value.strip('{}'))
        t.type = type_token[type(t.value)]
        return t

    @staticmethod
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'EQ', 'NE'),
        ('left', 'GE', 'GT', 'LE', 'LT'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
    )

    BINARY_OPERATORS = {
        'or': lambda a, b: a or b,
        'and': lambda a, b: a and b,
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,
        '<=': lambda a, b: a <= b,
        '>=': lambda a, b: a >= b,
        '!=': lambda a, b: a != b,
        '==': lambda a, b: a == b,
    }

    @staticmethod
    def p_not(p):
        'bool : NOT bool'
        p[0] = not p[2]

    @classmethod
    def p_binop(cls, p):
        """
        bool : number LT number
             | number GT number
             | number LE number
             | number GE number
             | number EQ number
             | number NE number
             | STRING EQ STRING
             | STRING NE STRING
             | bool OR bool
             | bool AND bool
        """
        # import pudb; pudb.set_trace()
        # check type consistency for numbers
        p[0] = cls.BINARY_OPERATORS[p[2]](p[1], p[3])

    @staticmethod
    def p_paren(p):
        """
        bool : LPAREN bool RPAREN
        container : LPAREN list RPAREN
        """
        p[0] = p[2]

    @staticmethod
    def p_self(p):
        """
        bool : BOOL
        number : INTEGER
               | FLOAT
        item : number
             | STRING
        listitem : item
                 | list
        """
        p[0] = p[1]

    @staticmethod
    def p_list(p):
        """
        list : listitem COMMA item
        """
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1], p[3]]

    @staticmethod
    def p_membership(p):
        """
        bool : item IN container
        """
        p[0] = p[1] in p[3]

    @staticmethod
    def p_membership_not(p):
        """
        bool : item NOT IN container
        """
        p[0] = p[1] not in p[4]

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

    def __init__(self, config):
        self.config = config
        self.names = {}
        lex.lex(module=self)
        yacc.yacc(module=self)

    def parse_string(self, s):
        return yacc.parse(s, debug=self.debug)
