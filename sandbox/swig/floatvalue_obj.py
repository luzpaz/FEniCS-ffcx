"This file implements a class to represent a float."

# Copyright (C) 2009-2010 Kristian B. Oelgaard
#
# This file is part of FFC.
#
# FFC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FFC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with FFC. If not, see <http://www.gnu.org/licenses/>.
#
# First added:  2009-07-12
# Last changed: 2010-01-21

# FFC common modules.
#from ffc.common.log import error

from new_symbol import CONST, format, create_float, create_product, create_fraction
from expr import Expr

# FFC common modules
from ffc.common.log import error

#import psyco
#psyco.full()

# TODO: This function is needed to avoid passing around the 'format', but could
# it be done differently?
def set_format(_format):
    global format
    format = _format
    global format_float
    format_float = format["floating point"]
    global EPS
    EPS = format["epsilon"]

class FloatValue(Expr):
    def __init__(self, value):
        """Initialise a FloatValue object, it derives from Expr and contains
        no additional variables.

        NOTE: self._prec = 0."""

        # Initialise value, type and class.
        self.val = float(value)
        self.t = CONST
        self._prec = 0

        # Handle zero value explicitly.
        if abs(value) <  EPS:
            self.val = 0.0

        # Compute the representation now, such that we can use it directly
        # in the __eq__ and __ne__ methods (improves performance a bit, but
        # only when objects are cached).
        self._repr = "FloatValue(%s)" % format_float(self.val)

        # Use repr as hash value
        self._hash = hash(self._repr)

    # Print function.
    def __str__(self):
        "Simple string representation which will appear in the generated code."
        return format_float(self.val)

    # Binary operators.
    def __add__(self, other):
        "Addition by other objects."
        # NOTE: We expect expanded objects here.
        # This is only well-defined if other is a float or if self.val == 0.
        if other._prec == 0: # float
            return create_float(self.val+other.val)
        elif self.val == 0.0:
            return other
        # Addition is not defined if self is not zero.
        # TODO: We could just return a Sum?
        error("Can only add two floats, or other to zero.")

    def __mul__(self, other):
        "Multiplication by other objects."
        # NOTE: We expect expanded objects here i.e., Product([FloatValue])
        # should not be present.
        # Only handle case where other is a float, else let the other
        # object handle the multiplication.
        if other._prec == 0: # float
            return create_float(self.val*other.val)
        return other.__mul__(self)

    def __div__(self, other):
        "Division by other objects."
        # If division is illegal (this should definitely not happen).
        if other.val == 0.0:
            error("Division by zero")

        # TODO: Should we also support division by fraction for generality?
        # It should not be needed by this module.
        if other._prec == 4: # frac
            error("Did not expected to divide by fraction")

        # If fraction will be zero.
        if self.val == 0.0:
            return self

        # NOTE: We expect expanded objects here i.e., Product([FloatValue])
        # should not be present.
        # Handle types appropriately.
        if other._prec == 0: # float
            return create_float(self.val/other.val)
        # If other is a symbol, return a simple fraction.
        elif other._prec == 1: # sym
            return create_fraction(self, other)
        # Don't handle division by sum.
        elif other._prec == 3: # sum
            # TODO: Here we could do: 4 / (2*x + 4*y) -> 2/(x + 2*y).
            return create_fraction(self, other)

        # If other is a product, remove any float value to avoid
        # 4 / (2*x), this will return 2/x.
        val = 1.0
        for v in other.vrs:
            if v._prec == 0: # float
                val *= v.val

        # If we had any floats, create new numerator and only use 'real' variables
        # from the product in the denominator.
        if val != 1.0:
            # Check if we need to create a new denominator.
            # TODO: Just use other.vrs[1:] instead.
            if len(other.get_vrs()) > 1:
                return create_fraction(create_float(self.val/val), create_product(other.get_vrs()))
            # TODO: Because we expect all products to be expanded we shouldn't need
            # to check for this case, just use other.vrs[1].
            elif len(other.get_vrs()) == 1:
                return create_fraction(create_float(self.val/val), other.vrs[1])
            error("No variables left in denominator")

        # Nothing left to do.
        return create_fraction(self, other)

from symbol_obj     import Symbol
from product_obj    import Product
from sum_obj        import Sum
from fraction_obj   import Fraction

