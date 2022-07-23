import abc
import logging
from typing import Optional, List, Generator

from gimeltune.models.configuration import Configuration
from gimeltune.search.algorithms import SearchAlgorithm

log = logging.getLogger(__name__)


class MetaSearchAlgorithm(SearchAlgorithm):

    def __init__(self, *algorithms, **kwargs):
        super().__init__(*algorithms, **kwargs)
        self.algorithms = list(algorithms)
        self.req_count = 0
        self.ask_gen = self._ask()

    def ask(self) -> Optional[List[Configuration]]:
        return next(self.ask_gen)

    def _ask(self) -> Generator:
        prev_picked = ''
        while True:
            for algo in self.order:
                if not prev_picked or prev_picked != algo.name:
                    log.debug(f'Pick {algo.name}')
                configs = algo.ask()
                yield configs
                self.req_count += 1 if configs is not None else 0
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

    @property
    @abc.abstractmethod
    def order(self):
        raise NotImplementedError()
