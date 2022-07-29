import logging
from collections import defaultdict, Counter

import numpy as np
from mab import algs

from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.meta import MetaSearchAlgorithm

log = logging.getLogger(__name__)


class UCB1(MetaSearchAlgorithm):

    STRATEGY = algs.UCB1

    def __init__(self, *algorithms, algo_select_count=3):
        super().__init__(*algorithms)
        self.mab = None
        self.name2index = dict()
        self.results = []
        self.algo_select_count: int = algo_select_count
        self.mult = 10
        self.rewards = Counter()

    def add_algorithm(self, algo):
        self.algorithms.append(algo)

    def remove_algorithm(self, algo: SearchAlgorithm):
        self.algorithms.remove(algo)
        self._fix_names()
        self.mab = self.STRATEGY(len(self.algorithms))
        self.name2index = {algo.name: i
                           for i, algo in enumerate(self.algorithms)}

        for algo_index, reward in self.rewards.items():
            for _ in range(reward):
                self.mab.reward(algo_index)

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
        index = max(len(self.algorithms), self.algo_select_count)
        ranking_chunk = ranking[:index]

        return [self.algorithms[i] for i in ranking_chunk]

    def tell(self, config, result):
        """Tell results to all search algorithms"""

        reward_multiplier = 1

        if len(self.results) % 10 == 0:
            log.debug(f'Up reward multiplier to {self.mult}')
            self.mult *= 2

        has_reward = False
        algo_index = None

        if np.isfinite(result) and config.requestor in self.name2index:
            algo_index = self.name2index[config.requestor]

            if self.results:
                m = min(self.results)
                relative_change = -(result - m)/m
                has_reward = relative_change > 0.005
                performance = relative_change * self.mult

                if np.isfinite(performance):
                    reward_multiplier = max(1, int(relative_change * self.mult))
                else:
                    reward_multiplier = 100
            else:
                has_reward = False

        if has_reward:
            for i in range(reward_multiplier):
                self.mab.reward(algo_index)
                self.rewards[algo_index] += 1
            log.debug(f'Reward <{reward_multiplier}> '
                      f'for {config.requestor} with result: {result}')

        self.results.append(result)

        for algo in self.algorithms:
            algo.tell(config, result)


class UCBTuned(UCB1):
    STRATEGY = algs.UCBTuned


class ThompsonSampler(UCB1):
    STRATEGY = algs.ThompsomSampling
