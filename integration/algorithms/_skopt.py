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
from typing import Generator
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.search.space import SearchSpace
from feijoa.utils.imports import ImportWrapper
from numpy import float64
from numpy import int64
from numpy.ma import MaskedArray
import sklearn.utils.fixes


sklearn.utils.fixes.MaskedArray = MaskedArray
# noinspection PyPackageRequirements
with ImportWrapper():
    import skopt

__all__ = ["SkoptBayesianAlgorithm"]


class SkoptBayesianAlgorithm(SearchAlgorithm):

    anchor = "skopt"
    aliases = ("Skopt", "SkoptBayesian", "skopt")

    def __init__(self, search_space: SearchSpace, **kwargs):

        super().__init__(**kwargs)

        self.skopt_space = self._make_space(search_space)
        self.optimizer_instance = skopt.Optimizer(
            self.skopt_space, "GBRT"
        )

        self.ask_generator: Optional[Generator] = None

    @staticmethod
    def _make_space(space: SearchSpace):
        params = []

        for p in space.params:
            if isinstance(p, Integer):
                params.append(
                    skopt.space.Integer(
                        name=p.name, low=p.low, high=p.high
                    )
                )
            elif isinstance(p, Real):
                params.append(
                    skopt.space.Real(
                        name=p.name, low=p.low, high=p.high
                    )
                )
            elif isinstance(p, Categorical):
                params.append(
                    skopt.space.Categorical(
                        name=p.name, categories=p.choices
                    )
                )

        return params

    def _ask(self, n: int) -> Generator:
        @skopt.utils.use_named_args(self.skopt_space)
        def named(**kwargs) -> dict:
            return kwargs

        while True:
            asked = list()
            raws = self.optimizer_instance.ask(n_points=n)

            for raw in raws:
                # FIXME (qnbhd) make correct work with numpy types
                potentially_cfg = dict()

                for k, v in named(raw).items():
                    if isinstance(v, int64):  # type: ignore
                        v = int(v)
                    if isinstance(v, (float, float64)):  # type: ignore
                        v = float(v)

                    potentially_cfg[k] = v

                asked.append(
                    Configuration(
                        potentially_cfg, requestor=self.name
                    )
                )

            yield asked

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self.ask_generator:
            self.ask_generator = self._ask(n)
        return next(self.ask_generator)

    def tell(self, config, result):
        self.optimizer_instance.tell(list(config.values()), result)
