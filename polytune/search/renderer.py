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
from polytune.search import Categorical, Integer, Real
from polytune.search.visitor import ParametersVisitor
from polytune.search.parameters import Categorical, Real, Parameter
from typing import Union


class Renderer(ParametersVisitor):
    def __init__(self, cfg):
        super().__init__()
        self.config = cfg

    def get_value(self, param: Parameter) -> Union[str, float]:
        value = self.config.data[param.name]
        return value

    def visit_common(self, p: Parameter) -> str:
        value = self.get_value(p)
        return f"{p.name}{value}"

    def visit_integer(self, p: Integer):
        return self.visit_common(p)

    def visit_real(self, p: Real) -> str:
        return self.visit_common(p)

    def visit_categorical(self, p: Categorical, **kwargs) -> str:
        value = self.get_value(p)
        return f"{value}"
