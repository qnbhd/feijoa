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


class Parameter(metaclass=abc.ABCMeta):

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        raise NotImplemented()

    def __str__(self):
        raise NotImplemented

    @abc.abstractmethod
    def accept(self, v):
        raise NotImplemented()


class Integer(Parameter):

    def __init__(self, name: str, *, low: int, high: int):
        super().__init__(name)
        self.low = low
        self.high = high

    def __repr__(self):
        return f"Integer {self.name}: [{self.low}, {self.high}]"

    def accept(self, v):
        return v.visit_integer(self)


class Real(Parameter):

    def __init__(self, name: str, *, low: float, high: float):
        super().__init__(name)
        self.low = low
        self.high = high

    def __repr__(self):
        return f"Real {self.name}: [{self.low}, {self.high}]"

    def accept(self, v):
        return v.visit_real(self)


class Categorical(Parameter):

    def __init__(self, name: str, *, choices):
        super().__init__(name)
        self.choices = choices

    def __repr__(self):
        return f"Categorical {self.name}: [{self.choices}]"

    def accept(self, v):
        return v.visit_categorical(self)
