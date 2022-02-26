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
import warnings
from typing import List

import yaml

from polytune.search.parameters import Categorical, Integer, Parameter, Real

__all__ = [
    'SearchSpace'
]


class SearchSpace:
    """Search (observation) space class"""

    def __init__(self):
        self.params: List[Parameter] = list()
        self.name2param = dict()

    def insert(self, p: Parameter) -> None:
        self.params.append(p)
        self.name2param[p.name] = p

    def get(self, item: str, default=None):
        return self.name2param.get(item, default=default)

    def __repr__(self) -> str:
        buff = ['SearchSpace:']

        for p in self.params:
            buff.append(f'\t{p}')

        return '\n'.join(buff)

    def __str__(self):
        return repr(self)

    def __iter__(self):
        return iter(self.params)

    @classmethod
    def from_yaml(cls, yaml_string):
        """Load search space from yaml file."""

        space_dumped = yaml.safe_load(yaml_string)

        space = SearchSpace()

        for p in space_dumped:
            loaded = parameter_factory(**p)
            space.insert(loaded)

        return space

    @classmethod
    def from_yaml_file(cls, yaml_file):
        with open(yaml_file) as f:
            return cls.from_yaml(f.read())


def parameter_factory(**kwargs):
    param_signature = kwargs["signature"]

    if kwargs["type"] == "integer":
        param_potentially_range = kwargs.get('range', None)
        if param_potentially_range is not None:
            low, high = param_potentially_range
        else:
            low, high = kwargs['low'], kwargs['high']
        return Integer(param_signature, low=low, high=high)
    elif kwargs["type"] == "real":
        return Real(param_signature, low=kwargs["low"], high=kwargs["high"])
    elif kwargs["type"] == "categorical":
        return Categorical(param_signature, choices=kwargs["choices"])

    raise TypeError()


def from_yaml(yaml_file: str) -> SearchSpace:
    """Load search space from yaml file."""

    warnings.warn('Function `from_yaml` is deprecated.'
                  'Use SearchSpace.from_yaml instead.',
                  DeprecationWarning)

    with open(yaml_file) as f:
        space_dumped = yaml.safe_load(f)

    space = SearchSpace()

    for p in space_dumped:
        loaded = parameter_factory(**p)
        space.insert(loaded)

    return space
