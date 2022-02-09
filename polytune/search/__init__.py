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
from polytune.search.parameters import Integer, Real, Categorical

from itertools import chain
from typing import Any, Dict

from polytune.search import Integer, Real

_RegisteredTypes: Dict[str, Any] = dict()


def register_type(type_name, type_cls, *aliases):
    for name in chain(type_name, aliases):
        _RegisteredTypes[name] = type_cls


register_type('integer', Integer, 'int')
register_type('real', Real, 'real')
register_type('categorical', Categorical, 'categorical')


def build_type_cls(name: str):
    return _RegisteredTypes[name]


class ArgExpectedException(BaseException):
    """Raises if some arg expected, but not founded."""


def ParameterFactory(**kwargs):
    param_signature = kwargs['signature']

    if kwargs['type'] == 'integer':
        return Integer(param_signature, low=kwargs['low'], high=kwargs['high'])
    elif kwargs['type'] == 'real':
        return Real(param_signature, low=kwargs['low'], high=kwargs['high'])
    elif kwargs['type'] == 'categorical':
        return Categorical(param_signature, choices=kwargs['choices'])

    raise TypeError()