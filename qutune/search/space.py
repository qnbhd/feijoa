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
import copy
from pprint import pformat
from typing import List

import skopt
import yaml

from qutune.search import ParameterFactory
from qutune.search.parameters import Parameter, Integer, Real, Categorical


class SearchSpace:

    def __init__(self):
        self.params: List[Parameter] = list()
        self.name2param = dict()

    def add_parameter(self, p: Parameter):
        self.params.append(p)
        self.name2param[p.name] = p

    def get_by_name(self, name):
        return self.name2param[name]

    def __repr__(self) -> str:
        representation = pformat(self.params).replace('\n', '\n\t')
        return f"SearchSpace(\n\t{representation}\n)"

    def to_skopt(self):
        params = []

        for p in self.params:
            if isinstance(p, Integer):
                params.append(skopt.space.Integer(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Real):
                params.append(skopt.space.Real(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Categorical):
                params.append(skopt.space.Categorical(name=p.name, categories=p.choices))

        return params



def from_yaml(yaml_file: str) -> SearchSpace:
    with open(yaml_file) as f:
        space_dumped = yaml.safe_load(f)

    space = SearchSpace()

    for p in space_dumped:
        loaded = ParameterFactory(**p)
        space.add_parameter(loaded)

    return space

