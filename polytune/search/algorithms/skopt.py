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
from typing import Generator, List, Optional

import sklearn.utils.fixes
from numpy import float64, int64
from numpy.ma import MaskedArray

from polytune.models import Experiment, ExperimentsFactory
from polytune.search.parameters import Categorical, Integer, Real
from polytune.search.space import SearchSpace

from . import SearchAlgorithm

sklearn.utils.fixes.MaskedArray = MaskedArray
# noinspection PyPackageRequirements
import skopt

__all__ = [
    'SkoptBayesianAlgorithm'
]


class SkoptBayesianAlgorithm(SearchAlgorithm):
    def __init__(self, search_space: SearchSpace,
                 experiment_factory: ExperimentsFactory, **kwargs):

        super().__init__(**kwargs)

        self.skopt_space = self._make_space(search_space)
        self.experiment_factory = experiment_factory
        self.optimizer_instance = skopt.Optimizer(self.skopt_space, "GBRT")

        self.ask_generator = self._ask()

    @property
    def per_emit_count(self):
        warnings.warn('Now per-emit count in skopt technique implemented not correctly.'
                      ' Per-emit count is property, return default value (1).')
        return 2

    @staticmethod
    def _make_space(space: SearchSpace):
        params = []

        for p in space.params:
            if isinstance(p, Integer):
                params.append(skopt.space.Integer(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Real):
                params.append(skopt.space.Real(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Categorical):
                params.append(
                    skopt.space.Categorical(name=p.name, categories=p.choices)
                )

        return params

    def _ask(self) -> Generator:
        @skopt.utils.use_named_args(self.skopt_space)
        def named(**kwargs):
            return kwargs

        while True:
            asked = list()

            for _ in range(self.per_emit_count):
                raw = named(self.optimizer_instance.ask())

                # FIXME (qnbhd) make correct work with numpy types
                potentially_cfg = dict()

                for k, v in raw.items():
                    if isinstance(v, int64):
                        v = int(v)
                    if isinstance(v, float64):
                        v = float(v)

                    potentially_cfg[k] = v

                cfg = self.experiment_factory.create(potentially_cfg)
                asked.append(cfg)

            yield asked

    def ask(self) -> Optional[List[Experiment]]:
        try:
            return next(self.ask_generator)
        except StopIteration:
            return None

    def tell(self, experiment: Experiment):
        self.optimizer_instance.tell(
            list(experiment.params.values()),
            experiment.objective_result
        )
