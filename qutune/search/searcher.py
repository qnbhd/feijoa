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
from collections import Coroutine

from numpy.ma import MaskedArray
import sklearn.utils.fixes

from qutune.search.renderer import Renderer

sklearn.utils.fixes.MaskedArray = MaskedArray

from qutune.environment import Environment
from qutune.search.space import SearchSpace
from workloads.workload import Workload

import skopt


class Searcher:

    def __init__(self, workload: Workload, space: SearchSpace):
        self.workload = workload
        self.space = space
        self.skopt_space = self.space.to_skopt()

        env = Environment()
        self.test_limit = env.test_limit
        self.test_count = 0

        self.opt = skopt.Optimizer(self.skopt_space)

        self.ask_coroutine = self._ask_coroutine()
        self.ask_coroutine.send(None)

        self.renderer = Renderer()

    def ask(self):
        try:
            # noinspection PyTypeChecker
            return next(self.ask_coroutine)
        except StopIteration:
            return None

    def _AskWrapper(self):
        @skopt.utils.use_named_args(self.skopt_space)
        def named(**kwargs):
            return kwargs

        while self.test_count < self.test_limit:
            cfg = self.opt.ask()

            d = dict()
            for p, value in named(cfg).items():
                d[self.space.get_by_name(p)] = value

            yield d
            self.test_count += 1

    def _ask_coroutine(self) -> Coroutine:
        yield from self._AskWrapper()

    def tell(self, suggested, result):
        self.opt.tell(suggested, result)

