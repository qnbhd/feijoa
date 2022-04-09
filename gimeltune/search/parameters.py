# MIT License
#
# Copyright (c) 2021 Templin Konstantin
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
import abc

__all__ = [
    'Parameter',
    'Integer',
    'Real',
    'Categorical',
    'ParametersVisitor'
]

from gimeltune.exceptions import ParametersIncorrectInputValues


class Parameter(metaclass=abc.ABCMeta):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        raise NotImplementedError()

    def __str__(self):
        return repr(self)

    @abc.abstractmethod
    def accept(self, v):
        raise NotImplementedError()

    @abc.abstractmethod
    def seed(self):
        raise NotImplementedError()


class Integer(Parameter):
    def __init__(self, name: str, *, low: int, high: int):
        super().__init__(name)

        if not isinstance(low, int) or not isinstance(high, int):
            raise ParametersIncorrectInputValues('Low and High bounds for'
                                                 ' Integer parameter'
                                                 ' must be ints.')

        self.low = low
        self.high = high

    def __repr__(self):
        return f"Integer('{self.name}, low={self.low}, high={self.high})"

    def accept(self, v):
        return v.visit_integer(self)

    def seed(self):
        return self.low


class Real(Parameter):
    def __init__(self, name: str, *, low: float, high: float):
        super().__init__(name)

        if not isinstance(low, float) or not isinstance(high, float):
            raise ParametersIncorrectInputValues('Low and High bounds for'
                                                 ' Float parameter'
                                                 ' must be floats.')

        self.low = low
        self.high = high

    def __repr__(self):
        return f"Real('{self.name}', {self.low=}, {self.high=}]"

    def accept(self, v):
        return v.visit_real(self)

    def seed(self):
        return self.low


class Categorical(Parameter):
    def __init__(self, name: str, *, choices):
        super().__init__(name)

        if not choices:
            raise ParametersIncorrectInputValues('Choices for Categorical'
                                                 ' parameter must be not empty.')
        self.choices = choices

    def __repr__(self):
        return f"Categorical('{self.name}', choices={self.choices})"

    def accept(self, v):
        return v.visit_categorical(self)

    def seed(self):
        return self.choices[0]


class ParametersVisitor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def visit_integer(self, p: Integer):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_real(self, p: Real):
        raise NotImplementedError()

    @abc.abstractmethod
    def visit_categorical(self, p: Categorical):
        raise NotImplementedError()
