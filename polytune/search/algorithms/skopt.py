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

from .algorithm import SearchAlgorithm
from polytune.search import Integer, Real, Categorical
from polytune.search.space import SearchSpace

import sklearn.utils.fixes
from numpy.ma import MaskedArray

sklearn.utils.fixes.MaskedArray = MaskedArray
import skopt
import polytune.environment as ENV


class SkoptBayesianAlgorithm(SearchAlgorithm):

    def __init__(self, search_space: SearchSpace, **kwargs):
        super().__init__(**kwargs)
        self.skopt_space = self._make_space(search_space)
        self.optimizer_instance = skopt.Optimizer(self.skopt_space, 'GBRT')
        self.per_emit_count = ENV.processes_count

        self.coroutine = self._ask()
        self.coroutine.send(None)

    @staticmethod
    def _make_space(space: SearchSpace):
        params = []

        for p in space.params:
            if isinstance(p, Integer):
                params.append(skopt.space.Integer(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Real):
                params.append(skopt.space.Real(name=p.name, low=p.low, high=p.high))
            elif isinstance(p, Categorical):
                params.append(skopt.space.Categorical(name=p.name, categories=p.choices))

        return params

    def _ask(self):
        @skopt.utils.use_named_args(self.skopt_space)
        def named(**kwargs):
            return kwargs

        while True:
            asked = [
                named(self.optimizer_instance.ask()) for _ in range(self.per_emit_count)
            ]
            yield asked

    def ask(self):
        try:
            return next(self.coroutine)
        except StopIteration:
            pass

    def tell(self, suggested, result):
        self.optimizer_instance.tell(suggested, result)
