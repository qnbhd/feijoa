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
from feijoa.search import SearchSpace

# noinspection PyProtectedMember,PyDeprecation
from feijoa.search.space import from_yaml
import pytest


def test_space_from_yaml():
    yaml = """- signature: -O
  type: categorical
  choices: [-O1, -O2, -O3, null]

- signature: align-functions
  type: categorical
  choices: [-falign-functions, -fno-align-functions, null]

- signature: iv-max-considered-uses
  type: integer
  range: [0, 1000]

- signature: foo
  type: integer
  low: 0
  high: 1000

- signature: boo
  type: real
  low: 0.0
  high: 1.0

- signature: zoo
  type: real
  range: [0.0, 10.0]
"""

    space = SearchSpace.from_yaml(yaml)

    assert space.get("boo").name == "boo"

    with open("foo.yaml", "w") as yf:
        yf.write(yaml)

    with pytest.deprecated_call():
        # noinspection PyDeprecation
        from_yaml("foo.yaml")

    space_from_file = SearchSpace.from_yaml_file("foo.yaml")

    assert (
        str(space)
        == """SearchSpace:
    Categorical('-O', choices=['-O1', '-O2', '-O3', None])
    Categorical('align-functions', choices=['-falign-functions', '-fno-align-functions', None])
    Integer('iv-max-considered-uses, low=0, high=1000)
    Integer('foo, low=0, high=1000)
    Real('boo', low=0.0, high=1.0)
    Real('zoo', low=0.0, high=10.0)"""
    )

    assert (
        str(space_from_file)
        == """SearchSpace:
    Categorical('-O', choices=['-O1', '-O2', '-O3', None])
    Categorical('align-functions', choices=['-falign-functions', '-fno-align-functions', None])
    Integer('iv-max-considered-uses, low=0, high=1000)
    Integer('foo, low=0, high=1000)
    Real('boo', low=0.0, high=1.0)
    Real('zoo', low=0.0, high=10.0)"""
    )


def test_incorrect_yaml_parameter_type():
    doc = """- signature: foo
  type: unknown
  low: 0
  high: 1000"""

    with pytest.raises(TypeError):
        SearchSpace.from_yaml(doc)
