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
        seed_algorithms = [
            a for a in self.algorithms if isinstance(a, SeedAlgorithm)
        ]

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
        """
        Append algorithm to algorithms list.

        :param algo: search algorithm instance.
        :return: None
        """

        self.algorithms.append(algo)

    @abc.abstractmethod
    def remove_algorithm(self, algo: SearchAlgorithm):
        """
        Remove algorithm from inner techniques
        pool in meta-technique.

        :param algo: search algorithm instance.
        :return: None.
        """

    @property
    @abc.abstractmethod
    def order(self):
        raise NotImplementedError()
