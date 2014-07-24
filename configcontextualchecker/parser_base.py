"""This module provides a parser for conditional expressions."""

from ply import lex, yacc

from .exceptions import ParserSyntaxError


class ParserBase(object):
    """This class provides a conditional expression parser."""

    debug = 0

    tokens = (
        'FLOAT',  # must be before INTEGER
        'INTEGER',
        'COMMA',
    )

    # Tokens
    t_COMMA = r','

    t_ignore = " \t"

    def __init__(self):
        # TODO: do we need a lexer object? (ADe 24/07/14)
        lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def parse_string(self, string):
        """Parse a string.

        Parameters
        ----------
        string : str
            string to be parsed

        Returns
        -------
        parsed object (derived class dependent)
        """
        return self.parser.parse(string, debug=self.debug)

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
        # TODO: use exception? (ADe 24/07/14)
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def p_error(self, p):
        raise ParserSyntaxError(p)
