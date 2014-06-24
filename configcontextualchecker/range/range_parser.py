"""This module provides a range parser."""

from pyparsing import oneOf, Literal, Regex

from .range import Range
from .bound import LowerBound, UpperBound


def _action_range(tokens):
    """Return a range object."""
    lower_is_open = tokens[0] == ']'
    lower_value = tokens[1]
    upper_value = tokens[2]
    upper_is_open = tokens[3] == '['
    if lower_value == LowerBound.UNBOUND:
        lower_value = None
    if upper_value == UpperBound.UNBOUND:
        upper_value = None
    return lower_value, lower_is_open, upper_value, upper_is_open


def _action_int(tokens):
    """Convert to int."""
    return int(tokens[0])


def _action_float(tokens):
    """Convert to float."""
    return float(tokens[0])


# define the range parsers
BRACKET = oneOf('[ ]')
INTEGER = Regex(r'[+-]?\d+').setParseAction(_action_int)
FLOAT = Regex(r'\d+\.\d*([eE]\d+)?').setParseAction(_action_float)
# float must be first so to catch the decimal separator
LEFT_TERM = FLOAT | INTEGER | Literal(LowerBound.UNBOUND)
RIGHT_TERM = FLOAT | INTEGER | Literal(UpperBound.UNBOUND)
RANGE = BRACKET + LEFT_TERM + Literal(',').suppress() + RIGHT_TERM + BRACKET
RANGE.setParseAction(_action_range)


def _get_range_args(string):
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
    return RANGE.parseString(string)[0]


def parse_range(string):
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
    return Range(*_get_range_args(string))
