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
import warnings
from typing import List, Coroutine, Optional

from polytune.models.experiment import Experiment, ExperimentsFactory
from polytune.search.algorithms.skopt import SkoptBayesianAlgorithm
from polytune.search.space import SearchSpace

log = logging.getLogger(__name__)


class Searcher:
    def __init__(self, space: SearchSpace, experiments_factory: ExperimentsFactory):
        self.space = space
        self.experiments_factory = experiments_factory

        self.search_algorithm = SkoptBayesianAlgorithm(space, self.experiments_factory)

        self.test_count = 0
        self.max_retries = 3

        self.ask_coroutine = self._ask_coroutine()
        self.ask_coroutine.send(None)

    def ask(self) -> Optional[List[Experiment]]:
        try:
            # noinspection PyTypeChecker
            return next(self.ask_coroutine)
        except StopIteration:
            return None

    def _ask_coroutine(self) -> Coroutine:
        retries = 0
        while retries != self.max_retries:
            suggested_configs_list = self.search_algorithm.ask()

            if suggested_configs_list is None:
                break

            yield suggested_configs_list

    def tell(self, experiment: Experiment) -> None:
        warnings.warn('Searcher.tell not implemented.')
        self.search_algorithm.tell(experiment)
