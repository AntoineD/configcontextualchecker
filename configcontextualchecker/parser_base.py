"""This module provides a parser for conditional expressions."""

from ply import lex, yacc


class ParserSyntaxError(SyntaxError):
    """This class provides a syntax error for the conditional parser."""

    MSG_EOS = 'syntax error at end of string'
    MSG_PATTERN = 'syntax error at "{}"\n{}\n{}'

    def __init__(self, parser):
        self.parser = parser

    def __str__(self):
        if self.parser is None:
            return self.MSG_EOS
        else:
            position = self.parser.lexpos
            lexdata = self.parser.lexer.lexdata
            pointer = '-' * position + '^' + \
                      '-' * (len(lexdata) - position - 1)
            return self.MSG_PATTERN.format(self.parser.value, lexdata, pointer)


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

    def __init__(self, config):
        self.config = config
        lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def parse_string(self, s):
        return self.parser(s, debug=self.debug)
