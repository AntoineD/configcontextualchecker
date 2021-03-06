"""This module provides a parser."""

from ply import lex, yacc

from .exceptions import ParserSyntaxError


class ParserBase(object):
    """This class provides a basic parser.

    It can parse:
    * a comma,
    * a float,
    * an integer,
    * ignored characters

    It also defines the parse method.
    """

    debug = False

    tokens = (
        'FLOAT',  # must be before INTEGER to catch decimal point
        'INTEGER',
        'COMMA',
    )

    # Tokens
    t_COMMA = r','

    t_ignore = " \t"

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self,
                                debug=self.debug,
                                write_tables=False)

    def parse(self, string):
        """Parse a string.

        Parameters
        ----------
        string : str
            string to be parsed

        Returns
        -------
        parsed object (derived class dependent)
        """
        return self.parser.parse(string, lexer=self.lexer, debug=self.debug)

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
