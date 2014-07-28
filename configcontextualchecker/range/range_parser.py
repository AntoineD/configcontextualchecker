"""This module provides the range parser."""

from ..parser_base import ParserBase
from .range import Range
from .bound import LowerBound, UpperBound


class RangeParser(ParserBase):
    """This class provides a range parser."""

    tokens = ParserBase.tokens + (
        'BRACKET',
        'PLUS_INF',
        'MINUS_INF',
    )

    t_BRACKET = r'\[|\]'
    t_PLUS_INF = r'\+inf'
    t_MINUS_INF = r'\-inf'

    @staticmethod
    def p_range(p):
        """
        range : BRACKET item COMMA item BRACKET
        """
        p[0] = p[2]
        lower_is_open = p[1] == ']'
        lower_value = p[2]
        upper_value = p[4]
        upper_is_open = p[5] == '['
        if lower_value == LowerBound.UNBOUND:
            lower_value = None
        if upper_value == UpperBound.UNBOUND:
            upper_value = None
        p[0] = (lower_value, lower_is_open, upper_value, upper_is_open)

    @staticmethod
    def p_item(p):
        """
        item : FLOAT
             | INTEGER
             | PLUS_INF
             | MINUS_INF
        """
        p[0] = p[1]

    def _get_range_args(self, string):
        """Determine the Range class init arguments.

        Parameters
        ----------
        string : str
            string to be parsed

        Returns
        -------
        list
            Range object init arguments
        """
        return super(RangeParser, self).parse(string)

    def parse(self, string):
        """Parse a range expression.

        Parameters
        ----------
        string : str
            string to be parsed

        Returns
        -------
        Range
            a Range object
        """
        return Range(*self._get_range_args(string))
