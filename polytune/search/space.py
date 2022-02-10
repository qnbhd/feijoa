from pprint import pformat
from typing import Union, List

import yaml

from polytune.search import ParameterFactory
from polytune.search.parameters import Categorical, Real, Parameter


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


def from_yaml(yaml_file: str) -> SearchSpace:
    with open(yaml_file) as f:
        space_dumped = yaml.safe_load(f)

    space = SearchSpace()

    for p in space_dumped:
        loaded = ParameterFactory(**p)
        space.add_parameter(loaded)

    return space
