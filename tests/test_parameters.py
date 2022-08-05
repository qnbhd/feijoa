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
from feijoa import Categorical
from feijoa import Integer
from feijoa import Real
from feijoa.exceptions import ParametersIncorrectInputValues
from feijoa.search.parameters import ParametersVisitor
import pytest


def test_parameters_constructing():

    with pytest.raises(ParametersIncorrectInputValues):
        Integer("x", low="foo", high="bar")

    with pytest.raises(ParametersIncorrectInputValues):
        Integer("x", low=0.1, high=10.0)

    with pytest.raises(ParametersIncorrectInputValues):
        Real("x", low="foo", high="bar")

    with pytest.raises(ParametersIncorrectInputValues):
        Real("x", low=1, high=2)

    with pytest.raises(ParametersIncorrectInputValues):
        Categorical("x", choices=[])

    with pytest.raises(ParametersIncorrectInputValues):
        Categorical("x", choices=["foo", "foo"])

    with pytest.raises(ParametersIncorrectInputValues):
        Integer("x", low=10, high=1)

    with pytest.raises(ParametersIncorrectInputValues):
        Real("x", low=10.0, high=1.0)


def test_parameters_seed():

    i = Integer("x", low=0, high=10)
    assert i.seed() == 0

    r = Real("y", low=1.0, high=10.0)
    assert r.seed() == 1.0

    c = Categorical("z", choices=["foo", "bar"])
    assert c.seed() == "foo"


def test_parameters_visitor():
    class FooVisitor(ParametersVisitor):
        def visit_integer(self, p: Integer):
            return f"integer {p.name}"

        def visit_real(self, p: Real):
            return f"real {p.name}"

        def visit_categorical(self, p: Categorical):
            return f"categorical {p.name}"

    parameters = [
        Integer("x", low=0, high=10),
        Real("y", low=0.0, high=1.0),
        Categorical("z", choices=["foo", "bar"]),
    ]

    visitor = FooVisitor()
    ans = [p.accept(visitor) for p in parameters]

    assert ans == ["integer x", "real y", "categorical z"]
