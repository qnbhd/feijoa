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
import logging
from contextlib import suppress
from typing import Coroutine, List, Optional

from polytune.models.experiment import Experiment, ExperimentsFactory
from polytune.search.algorithms.algorithm import SearchAlgorithm
from polytune.search.algorithms.skopt import SkoptBayesianAlgorithm
from polytune.search.space import SearchSpace

log = logging.getLogger(__name__)

__all__ = [
    'Optimizer'
]


class Optimizer:
    def __init__(self, space: SearchSpace, experiments_factory: ExperimentsFactory):
        self.space = space
        self.experiments_factory = experiments_factory
        self.algorithms: List[SearchAlgorithm] = list()

        self._ask_coro = None

    def add_algorithm(self, algo: SearchAlgorithm):
        self.algorithms.append(algo)

    def ask(self) -> Optional[List[Experiment]]:
        if not self._ask_coro:
            self._ask_coro = self._ask_coroutine()
            self._ask_coro.send(None)

        try:
            # noinspection PyTypeChecker
            return next(self._ask_coro)
        except StopIteration:
            return None

    def _ask_coroutine(self) -> Coroutine:

        assert self.algorithms, 'Algorithms must be in list'

        while self.algorithms:

            algorithm = self.algorithms.pop(0)

            print(algorithm.__class__.__name__)

            with suppress(StopIteration):
                configs = algorithm.ask()

                print('GET FROM TECHNIQUE: ', configs)

                if not configs:
                    continue

                # Round Robin
                self.algorithms.append(algorithm)

                yield configs

    def tell(self, experiment: Experiment) -> None:
        for algo in self.algorithms:
            algo.tell(experiment)
