from ply import lex, yacc


class ParserError(Exception):
    pass


class Parser(object):

    tokens = (
        'BOOL',
        'NOT',
        'AND',
        'OR',
        'LPAREN',
        'RPAREN',
        # 'NAME', 'NUMBER',
    )

    # Tokens
    t_NOT = r'not'
    t_AND = r'and'
    t_OR = r'or'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    # t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    t_ignore = " \t"

    def __init__(self, config):
        self.config = config
        self.names = {}
        lex.lex(module=self)
        yacc.yacc(module=self)

    def parse_string(self, s):
        return yacc.parse(s)

    def run(self):
        while True:
            try:
                s = raw_input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            print self.parse_string(s)

    def t_BOOL(self, t):
        r'True|False'
        t.value = eval(t.value)
        return t

    # def t_NUMBER(self, t):
    #     r'\d+'
    #     try:
    #         t.value = int(t.value)
    #     except ValueError:
    #         print("Integer value too large %s" % t.value)
    #         t.value = 0
    #     # print "parsed number %s" % repr(t.value)
    #     return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        # ('left', 'PLUS', 'MINUS'),
        # ('left', 'TIMES', 'DIVIDE'),
        # ('right', 'UMINUS'),
    )

    # def p_statement_assign(self, p):
    #     'statement : NAME EQUALS expression'
    #     self.names[p[1]] = p[3]

    def p_expression_binop(self, p):
        """
        expression : expression OR expression
                  | expression AND expression
        """
        if p[2] == 'or':
            p[0] = p[1] or p[3]
        elif p[2] == 'and':
            p[0] = p[1] and p[3]

    def p_expression_not(self, p):
        'expression : NOT expression %prec NOT'
        p[0] = not p[2]

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_bool(self, p):
        'expression : BOOL'
        p[0] = p[1]

    # def p_expression_name(self, p):
    #     'expression : NAME'
    #     try:
    #         p[0] = self.names[p[1]]
    #     except LookupError:
    #         print("Undefined name '%s'" % p[1])
    #         p[0] = 0
    #
    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = Parser(None)
    calc.run()
