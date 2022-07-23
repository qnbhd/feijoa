import logging

from mab import algs

from gimeltune.search.meta import MetaSearchAlgorithm

log = logging.getLogger(__name__)


class UCB1(MetaSearchAlgorithm):

    STRATEGY = algs.UCB1

    def __init__(self, *algorithms, algo_select_count=3):
        super().__init__(*algorithms)
        self.mab = None
        self.name2index = dict()
        self.results = []
        self.algo_select_count: int = algo_select_count

    def add_algorithm(self, algo):
        self.algorithms.append(algo)

    def _fix_names(self):
        names = set()
        for a in self.algorithms:
            while a.name in names:
                a.name += '@'
            names.add(a.name)

    @property
    def order(self):
        if not self.mab:
            self._fix_names()
            self.mab = self.STRATEGY(len(self.algorithms))
            self.name2index = {algo.name: i
                               for i, algo in enumerate(self.algorithms)}

        arm, ranking = self.mab.select()
        index = min(len(self.algorithms), self.algo_select_count)
        ranking_chunk = ranking[:index]

        return [self.algorithms[i] for i in ranking_chunk]

    def tell(self, config, result):
        """Tell results to all search algorithms"""

        if config.requestor in self.name2index:
            algo_index = self.name2index[config.requestor]
            has_reward = 1 if not self.results else int(result < min(self.results))

            if has_reward:
                self.mab.reward(algo_index)
                log.debug(f'Reward for {config.requestor} with result: {result}')

        self.results.append(result)

        for algo in self.algorithms:
            algo.tell(config, result)


class UCBTuned(UCB1):
    STRATEGY = algs.UCBTuned


class ThompsonSampler(UCB1):
    STRATEGY = algs.ThompsomSampling
