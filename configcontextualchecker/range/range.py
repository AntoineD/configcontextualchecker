"""This module defines the value range class :class:`Range`."""

import types

from .bound import LowerBound, UpperBound


class Range(object):
    """This class implements a value range container.

    Used for checking whether a value belongs to a range.
    The checking is performed by using the contained operator, i.e.
    'value in range'. Lower and upper bounds values must be of the same type.

    Parameters
    ----------
    lower_value : int or float or None
        lower bound value
    lower_is_open : bool
        whether lower bound is open
    upper_value : int or float or None
        upper bound value
    upper_is_open : bool
        whether upper bound is open

    Attributes
    ----------
    lower : LowerBound
        lower bound
    upper : UpperBound
        upper bound
    """

    def __init__(self, lower_value, lower_is_open, upper_value, upper_is_open):
        self._check_bounds_values(lower_value, upper_value)
        self.lower = LowerBound(lower_value, lower_is_open)
        self.upper = UpperBound(upper_value, upper_is_open)

    @property
    def type(self):
        """Return the bound type."""
        # bound values are both of the same type or one is None
        if self.lower._value is not None:
            return type(self.lower._value)
        elif self.upper._value is not None:
            return type(self.upper._value)

    @staticmethod
    def _check_bounds_values(lower_value, upper_value):
        """Check the bound values.

        Parameters
        ----------
        lower_value, upper_value : int or float or None
            bound values

        Raises
        ------
        TypeError
            if the values are both numeric and have different types
        ValueError
            if the values are equal or lower > upper
        """
        types_ = set((type(lower_value), type(upper_value)))
        try:
            # remove None to simplify further checking
            types_.remove(types.NoneType)
            has_None = True
        except KeyError:
            has_None = False

        if tuple(types_) not in ((int,), (float,)):
            msg = 'incompatible types of the lower and upper bounds values: ' \
                  'type(lower) = {} and type(upper) = {}'.format(lower_value,
                                                                 upper_value)
            raise TypeError(msg)
        elif has_None:
            # one value is None so no further checks
            return

        if lower_value == upper_value:
            msg = 'lower and upper bounds are equal: ' \
                  'lower = upper = {}'.format(lower_value)
            raise ValueError(msg)

        elif lower_value > upper_value:
            msg = 'lower bound is greater than upper bounds: ' \
                  'lower = {} and upper = {}'.format(lower_value, upper_value)
            raise ValueError(msg)

    def __contains__(self, value):
        """Check a value is in the range.

        Parameters
        ----------
        value : int or float
            value to be checked

        Returns
        -------
        bool
            True if the value is within the range, False otherwise
        """
        return self.lower.check(value) and self.upper.check(value)

    def __repr__(self):
        return '{}, {}'.format(self.lower, self.upper)

    def __eq__(self, other):
        # there is a one to one mapping from string representation to
        # the object
        return str(self) == str(other)
