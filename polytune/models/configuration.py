import hashlib
import json

from polytune.search.renderer import Renderer
from polytune.search.space import SearchSpace
from typing import Dict, Type, Union

from pydantic import BaseModel


class Configuration(BaseModel):
    data: dict

    def __repr__(self):
        return f"Configuration({str(self.data)[1:-1]})"

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        encoded = json.dumps(self.data, sort_keys=True).encode()
        return hash(encoded)

    def render(self, space: SearchSpace, renderer_cls: Type[Renderer]) -> str:
        renderer = renderer_cls(self)

        rendered = list()

        for p_name in self.data.keys():
            p = space.get_by_name(p_name)
            result = p.accept(renderer)
            rendered.append(result)

        return " ".join(rendered)
