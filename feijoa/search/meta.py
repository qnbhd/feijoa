# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
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
"""Meta algorithm base class module."""

import abc
import logging
from typing import Generator
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.seed import SeedAlgorithm


log = logging.getLogger(__name__)


class MetaSearchAlgorithm(SearchAlgorithm):
    """Meta-search algorithm.

    Used for pick up algorithms.

    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(self, *algorithms, **kwargs):
        super().__init__(*algorithms, **kwargs)
        self.algorithms = list(algorithms)
        self.ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self.ask_gen:
            self.ask_gen = self._ask(n)
        return next(self.ask_gen)

    def _ask(self, n: int) -> Generator:
        prev_picked = ""

        # pick up all seed's algorithms

        seed_algorithms = [
            a for a in self.algorithms if isinstance(a, SeedAlgorithm)
        ]

        # remove all seed's algorithms

        for algo in seed_algorithms:
            self.remove_algorithm(algo)

        if seed_algorithms:
            log.debug("Let's measure seed configurations!")
            for algo in seed_algorithms:
                configs = algo.ask(n)
                yield configs

        while True:
            for algo in self.order:
                if not prev_picked or prev_picked != algo.name:
                    log.debug(f"Pick {algo.name}")
                configs = algo.ask(n)
                yield configs
                prev_picked = algo.name

    def tell(self, config, result):
        """Tell results to all search algorithms"""

        for algo in self.algorithms:
            algo.tell(config, result)

    def add_algorithm(self, algo: SearchAlgorithm):
        """Append algorithm to algorithms list.

        Args:
            algo (SearchAlgorithm):
                search algorithm instance.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        self.algorithms.append(algo)

    @abc.abstractmethod
    def remove_algorithm(self, algo: SearchAlgorithm):
        """Remove algorithm from inner techniques
        pool in meta-technique.

        Args:
            algo (SearchAlgorithm):
                search algorithm instance.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

    @property
    @abc.abstractmethod
    def order(self):
        """Get order for algorithms."""

        raise NotImplementedError()
