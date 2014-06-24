"""This module defines the exceptions used by configcontextualchecker."""


class RuleError(Exception):
    pass


class ItemError(Exception):
    pass


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
