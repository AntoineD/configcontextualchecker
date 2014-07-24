"""This module defines the exceptions used by configcontextualchecker."""


class RuleError(Exception):
    pass


class ItemError(Exception):
    pass


class ParserSyntaxError(SyntaxError):
    """This class provides a syntax error for the conditional parser."""

    MSG_EOS = 'syntax error at end of string'
    MSG_PATTERN = 'syntax error at "{}"\n{}\n{}'

    def __init__(self, parser):
        """
        Parameters
        ----------
        parser : parser object
            parser that raised the error
        """
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


# class DependencyError(Exception):
#     """Error class for the dependency scanner."""
#
#     def __init__(self, msg, key=None):
#         """
#         Parameters
#         ----------
#         msg : str
#             exception message
#         key : str, optional
#             node's key
#         """
#         super(DependencyError, self).__init__(msg)
#         self.key = key
#
#     def __str__(self):
#         msg = super(DependencyError, self).__str__()
#         if self.key is None:
#             return msg
#         else:
#             return 'key {}: {}'.format(self.key, msg)
#
# class GraphNodeError(Exception):
#
#     def __init__(self, msg, key=None):
#         """
#         Parameters
#         ----------
#         msg : str
#             exception message
#         key : str, optional
#             node's key
#         """
#         super(GraphNodeError, self).__init__(msg)
#         self.key = key
#
#     def __str__(self):
#         msg = super(GraphNodeError, self).__str__()
#         if self.key is None:
#             return msg
#         else:
#             return 'key {}: {}'.format(self.key, msg)
#
