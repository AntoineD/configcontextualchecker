"""This module provides a parser for conditional expressions."""

from ply import lex, yacc

from .exceptions import ParserSyntaxError


class ParserBase(object):
    """This class provides a conditional expression parser."""

    tokens = (
        'FLOAT',  # must be before INTEGER
        'INTEGER',
        'COMMA',
    )

    # Tokens
    t_COMMA = r','

    t_ignore = " \t"

    def __init__(self):
        lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    @staticmethod
    def t_FLOAT(t):
        r'\d+\.\d*([eE]\d+)?'
        t.value = eval(t.value)
        return t

    @staticmethod
    def t_INTEGER(t):
        r'[+-]?\d+'
        t.value = eval(t.value)
        return t

    @staticmethod
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules
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

    def p_error(self, p):
        raise ParserSyntaxError(p)
    def parse_string(self, s):
        return self.parser(s, debug=self.debug)
