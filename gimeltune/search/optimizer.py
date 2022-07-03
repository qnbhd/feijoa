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
from typing import Generator, List, Optional

from gimeltune.models.experiment import Experiment, ExperimentsFactory
from gimeltune.search.algorithms.algorithm import SearchAlgorithm
from gimeltune.search.space import SearchSpace

log = logging.getLogger(__name__)

__all__ = ["Optimizer"]


class Optimizer:
    """
    Experiment's optimizer class.

    Optimizer has two main methods:

    Parameters:
        - space
        - experiments_factory
    """
    def __init__(self, space: SearchSpace,
                 experiments_factory: ExperimentsFactory):
        self.space = space
        self.experiments_factory = experiments_factory
        self.algorithms: List[SearchAlgorithm] = list()
        self._ask_generator = None

    def add_algorithm(self, algo: SearchAlgorithm):
        """
        Append algorithm to algorithms list.

        :param algo: search algorithm instance.
        :return: None
        """

        self.algorithms.append(algo)

    def ask(self) -> Optional[List[Experiment]]:
        """
        Optimizer experiments ask method.

        :return: list of experiments or None if
                 no new experiments available.
        """

        self._ask_generator = self._ask_generator or self._ask()

        try:
            # noinspection PyTypeChecker
            return next(self._ask_generator)
        except StopIteration:
            return None

    def _ask(self) -> Generator:

        assert self.algorithms, "Algorithms must be in list"

        while self.algorithms:

            algorithm = self.algorithms.pop(0)

            configs = algorithm.ask()

            if not configs:
                continue

            for c in configs:
                c.requestor = algorithm.__class__.__name__

            # Round Robin
            self.algorithms.append(algorithm)

            yield configs

    def tell(self, experiment: Experiment) -> None:
        """Tell results to all search algorithms"""

        for algo in self.algorithms:
            algo.tell(experiment)
