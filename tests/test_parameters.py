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
