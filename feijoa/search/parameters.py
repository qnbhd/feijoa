# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Parameters module."""

import abc


__all__ = [
    "Parameter",
    "Integer",
    "Real",
    "Categorical",
    "ParametersVisitor",
]

from feijoa.exceptions import ParametersIncorrectInputValues


class Parameter(metaclass=abc.ABCMeta):
    """Base class of parameter."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        raise NotImplementedError()

    def __str__(self):
        return repr(self)

    @abc.abstractmethod
    def accept(self, v):
        """Accept visitor.

        Args:
            v (Visitor):
                ParametersVisitor instance.

        Returns:
            Any

        """

        raise NotImplementedError()

    @abc.abstractmethod
    def seed(self):
        """Make some legal value."""

        raise NotImplementedError()

    @abc.abstractmethod
    def is_primitive(self):
        """Primitive parameter, such as integer, real."""

        raise NotImplementedError()

    @abc.abstractmethod
    def get_unit_value(self, value):
        """Only for primitive parameters."""

        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def meta(self):
        """Meta information of parameter."""

        raise NotImplementedError()


class Integer(Parameter):
    """Integer parameter class.

    Represents discrete integer parameters from Z-space.

    Such parameters can be, for example, the number of
    layers in neural networks or the number of neurons
    in a hidden layer, max depth of tree.

    Example:

    .. code-block:: python

        from feijoa.search.parameters import Integer

        param = Integer("foo", low=0, high=10)

    .. note:
        In parameters creation strict-typing is used
        for input values.

    Args:
        name (str):
            Name of parameter.
        low (int):
            Lower bound of parameter.
        high (int):
            Upper bound of parameter.

    Raises:
        ParametersIncorrectInputValues:
            If input values is not valid integer values.
        AnyError:
            If anything bad happens.

    """

    def __init__(self, name: str, *, low: int, high: int):
        super().__init__(name)

        if not isinstance(low, int) or not isinstance(high, int):
            raise ParametersIncorrectInputValues(
                "Low and High bounds for"
                " Integer parameter"
                " must be ints."
            )
        if low > high:
            raise ParametersIncorrectInputValues(
                "High bound must" " be greater than low bound."
            )

        self.low = low
        self.high = high

    def __repr__(self):
        return (
            f"Integer('{self.name}, low={self.low}, high={self.high})"
        )

    def accept(self, v):
        return v.visit_integer(self)

    def seed(self):
        return self.low

    def is_primitive(self):
        return True

    def get_unit_value(self, value):
        return float(value - (self.low - 0.4999)) / float(
            (self.high + 0.4999) - (self.low - 0.4999)
        )

    @property
    def meta(self):
        m = {
            "low": self.low,
            "high": self.high,
        }
        return m


class Real(Parameter):
    """Real parameter class.

    Represents real parameters from R-space.

    Such parameters can be, for example, learning
    rate of ML algorithm, or mutation rate in
    genetic algorithms.

    Example:

    .. code-block:: python

        from feijoa.search.parameters import Real

        param = Real("foo", low=0.0, high=10.0)

    Args:
        name (str):
            Name of parameter.
        low (float):
            Lower bound of parameter.
        high (float):
            Upper bound of parameter.

    .. note:
        In parameters creation strict-typing is used
        for input values.

    Raises:
        ParametersIncorrectInputValues:
            If input values is not valid real values.
        AnyError:
            If anything bad happens.

    """

    def __init__(self, name: str, *, low: float, high: float):
        super().__init__(name)

        if not isinstance(low, float) or not isinstance(high, float):
            raise ParametersIncorrectInputValues(
                "Low and High bounds for"
                " Float parameter"
                " must be floats."
            )

        if low > high:
            raise ParametersIncorrectInputValues(
                "High bound must" " be greater than low bound."
            )

        self.low = low
        self.high = high

    def __repr__(self):
        return (
            f"Real('{self.name}', low={self.low}, high={self.high})"
        )

    def accept(self, v):
        return v.visit_real(self)

    def seed(self):
        return self.low

    def is_primitive(self):
        return True

    def get_unit_value(self, value):
        return float(value - self.low) / float(self.high - self.low)

    @property
    def meta(self):
        m = {
            "low": self.low,
            "high": self.high,
        }
        return m


class Categorical(Parameter):
    """Categorical parameter class.

    Represents category parameters.

    Such parameters can be, activation function,
    or type of regression model in AutoML.

    Args:
        name (str):
            Name of parameter.
        choices (list):
            List of choices, for example: ```['rbf', 'sigmoid']```

    .. note:
        In parameters creation strict-typing is used
        for input values.

    Raises:
        ParametersIncorrectInputValues:
            If input values is empty or exists
            not unique values.
        AnyError:
            If anything bad happens.

    """

    def __init__(self, name: str, *, choices):
        super().__init__(name)

        if not choices:
            raise ParametersIncorrectInputValues(
                "Choices for Categorical"
                " parameter must be not empty."
            )
        if len(choices) != len(set(choices)):
            raise ParametersIncorrectInputValues(
                "Choices for Categorical" " parameter must unique."
            )
        self.choices = choices

    def __repr__(self):
        return f"Categorical('{self.name}', choices={self.choices})"

    def accept(self, v):
        return v.visit_categorical(self)

    def seed(self):
        return self.choices[0]

    def is_primitive(self):
        return False

    def get_unit_value(self, value):
        raise NotImplementedError()

    @property
    def meta(self):
        m = {"choices": self.choices}
        return m


class ParametersVisitor(metaclass=abc.ABCMeta):
    """Parameters abstract visitor

    Used for iteration over collections
    with parameters.

    Raises:
        AnyError:
            If anything bad happens.

    """

    @abc.abstractmethod
    def visit_integer(self, p: Integer):
        """Visit integer parameter."""

        raise NotImplementedError()

    @abc.abstractmethod
    def visit_real(self, p: Real):
        """Visit real parameter."""

        raise NotImplementedError()

    @abc.abstractmethod
    def visit_categorical(self, p: Categorical):
        """Visit categorical parameter."""

        raise NotImplementedError()
