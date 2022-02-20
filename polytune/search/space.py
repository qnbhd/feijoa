from pprint import pformat
from typing import List, Union

import yaml

from polytune.search.parameters import Categorical, Integer, Parameter, Real

__all__ = [
    'SearchSpace'
]


class SearchSpace:
    def __init__(self):
        self.params: List[Parameter] = list()
        self.name2param = dict()

    def add_parameter(self, p: Parameter) -> None:
        self.params.append(p)
        self.name2param[p.name] = p

    def get_by_name(self, name: str) -> Union[Real, Categorical]:
        return self.name2param[name]

    def __repr__(self) -> str:
        representation = pformat(self.params).replace("\n", "\n\t")
        return f"SearchSpace(\n\t{representation}\n)"

    def __iter__(self):
        return iter(self.params)


class ArgExpectedException(BaseException):
    """Raises if some arg expected, but not founded."""


def ParameterFactory(**kwargs):
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
    with open(yaml_file) as f:
        space_dumped = yaml.safe_load(f)

    space = SearchSpace()

    for p in space_dumped:
        loaded = ParameterFactory(**p)
        space.add_parameter(loaded)

    return space
