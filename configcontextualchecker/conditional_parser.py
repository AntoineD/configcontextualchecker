"""This module is used for parsing conditional expressions."""


from pyparsing import infixNotation, opAssoc, QuotedString, \
    oneOf, Literal, Suppress, ParseException, \
    Regex, quotedString, removeQuotes, delimitedList, Word, \
    alphanums

from .dict_path import get_from_path


class ParserError(Exception):
    pass


# module global variable that holds the dict config
_config = None


def set_buffer(config):
    """Set the module config.

    Parameters
    ----------
    config : dict
        config object used to get values bound to dependencies
    """
    global _config
    _config = config


def parse_string(string, config=None):
    """Parse a string.

    Parameters
    ----------
    string : str
        a string to parse
    config : dict, optional
        config object

    Returns
    -------
    bool
        truth value of the conditional expression

    Raises
    ------
    ParserError
       if there is a parsing error
    """
    global _config
    _config = config or _config
    try:
        parsed = _parser.parseString(string)
    except ParseException as err:
        column = ' '*(err.column-1)
        msg = '{}\n{}\n{}^'.format(err.msg, err.line, column)
        raise ParserError(msg)
    else:
        return parsed[0]


# @traceParseAction
def _action_item(tokens):
    """Return the value bound to the key in config."""
    return get_from_path(_config, tokens[0])


# @traceParseAction
def _action_contain(tokens):
    """Return whether an item is contained in a list."""
    item = tokens[0]
    container = _type_variables(tokens[2:], type_=type(item))
    if tokens[1] == 'in':
        return item in container
    elif tokens[1] == 'not in':
        return item not in container


# @traceParseAction
def _action_comparison(tokens):
    """Return the result of a comparison."""
    operators = tokens[1::2]
    values = _type_variables(tokens[::2])
    val1 = values[0]
    for op, val in zip(operators, values[1:]):
        val2 = val
        if not COMPARISON_OPERATORS[op](val1, val2):
            return False
        val1 = val2

    return True


def _action_and(tokens):
    """Return whether and condition is true."""
    return all(tokens[0][0::2])


def _action_or(tokens):
    """Return whether or condition is true."""
    return any(tokens[0][0::2])


def _action_not(tokens):
    """Return whether not condition is true."""
    return not tokens[0][1]


def _action_variable(tokens):
    """Return the evaluation of a variable passed as a string."""
    return eval(tokens[0])


def _type_variables(sequence, type_=str):
    """Return consistently typed objects.

    Parameters
    ----------
    sequence : list or tuple
        sequence of objects
    type_ : int or float or str, optional
        excepted type, optional

    Returns
    -------
    list of type
        typed sequence

    Raises
    ------
    TypeError
        if the type is non unique.
    """
    # look for items that are not strings, if any
    types = map(type, sequence) + [type_]
    nonstr = [t for t in types if t != str]
    # determine if those non string objects have a consistent type
    unique_type = tuple(set(nonstr))
    if len(unique_type) > 1:
        # TODO: better msg
        raise TypeError('non unique type')
    elif len(unique_type) == 0:
        type_ = str
    else:
        type_ = unique_type[0]
    try:
        return map(type_, sequence)
    except ValueError:
        raise TypeError('non consistent type')

# define the parser elements
BOOL = oneOf('True False')
BOOL.setParseAction(_action_variable)

INTEGER = Regex(r'[+-]?\d+')
FLOAT = Regex(r'\d+\.\d*([eE]\d+)?')

STRING = quotedString
STRING.setParseAction(removeQuotes)

ITEM = QuotedString(quoteChar='{', endQuoteChar='}')
ITEM.setParseAction(_action_item)

# float must be first so to catch the decimal separator
OPERAND = FLOAT | INTEGER | STRING | Word(alphanums + '=_-')
LIST = Suppress('(') + delimitedList(OPERAND) + Suppress(')')
TERM = OPERAND | ITEM

CONTAIN_EXPR = ITEM + (Literal('in') | Literal('not in')) + LIST
CONTAIN_EXPR.setParseAction(_action_contain)

COMPARISON_EXPR = TERM + (oneOf('< <= > >= != ==') + TERM)*(1, 2)
COMPARISON_EXPR.setParseAction(_action_comparison)

# give the parser elements names for easier debugging
# INTEGER.setName('integer')
# FLOAT.setName('float')
# STRING.setName('string')
# OPERAND.setName('operand')
# LIST.setName('list')
# ITEM.setName('item')
# CONTAIN_EXPR.setName('contain')
# COMPARISON_EXPR.setName('comparison')

# CONTAIN_EXPR.setDebug()
# COMPARISON_EXPR.setDebug()

COMPARISON_OPERATORS = {
    '<': lambda a, b: a < b,
    '>': lambda a, b: a > b,
    '<=': lambda a, b: a <= b,
    '>=': lambda a, b: a >= b,
    '!=': lambda a, b: a != b,
    '==': lambda a, b: a == b,
    }

# assemble the parser
_condition_operand = CONTAIN_EXPR | COMPARISON_EXPR | BOOL
_parser = infixNotation(
    _condition_operand,
    [
        ('not', 1, opAssoc.RIGHT, _action_not),
        ('and', 2, opAssoc.LEFT, _action_and),
        ('or', 2, opAssoc.LEFT, _action_or),
    ]
)
# _parser.setDebug()
