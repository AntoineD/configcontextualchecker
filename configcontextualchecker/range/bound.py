"""This module defines the range bounds classes :class:`LowerBound` and :class:`UpperBound`."""

import operator


class BoundBase(object):
    """Base class for range bounds.

    A bound value set to None means no bound or infinite.

    Parameters
    ----------
    value : int or float
        bound value
    is_open : bool
        whether the bound is open or not

    Attributes
    ----------
    UNBOUND : str
        unbound identifier
    """

    # map is_open to an operator function used for comparing a value to
    # the bound's value
    _OPERATOR = None

    UNBOUND = None

    def __init__(self, value, is_open):
        self._value = value
        self._open = is_open

    @classmethod
    def _repr_unbound(cls, value):
        """Provide a string representation of a bound.

        Parameters
        ----------
        value : int or float or None
            bound value

        Returns
        -------
            representable bound value
        """
        if value is None:
            return cls.UNBOUND
        else:
            return value

    def check(self, value):
        """Check the value against the bound.

        Parameters
        ----------
        value : int or float
            value to be checked

        Returns
        -------
        bool
            whether the value satisfies the bound or not
        """
        if self._value is None:
            # no bound so it's always OK
            return True
        else:
            return self._OPERATOR[self._open](value, self._value)


class LowerBound(BoundBase):
    """Class representing a lower bound."""

    _OPERATOR = {
        True: operator.gt,
        False: operator.ge,
    }

    UNBOUND = '-inf'

    def __str__(self):
        v = self._repr_unbound(self._value)
        s = {
            True: ']',
            False: '[',
        }
        return '{}{}'.format(s[self._open], v)


class UpperBound(BoundBase):
    """Class representing a upper bound."""

    _OPERATOR = {
        True: operator.lt,
        False: operator.le,
    }

    UNBOUND = '+inf'

    def __str__(self):
        v = self._repr_unbound(self._value)
        s = {
            True: '[',
            False: ']',
        }
        return '{}{}'.format(v, s[self._open])
