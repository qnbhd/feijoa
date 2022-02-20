import warnings
from typing import Optional, List

from polytune.models.experiment import Experiment
from polytune.search.parameters import Categorical, Real, Integer, ParametersVisitor
from polytune.search.algorithms import SearchAlgorithm
import random

__all__ = [
    'RandomSearch'
]


class Randomizer(ParametersVisitor):

    def visit_integer(self, p: Integer):
        return random.randint(p.low, p.high)

    def visit_real(self, p: Real):
        return p.high * random.random() + p.low

    def visit_categorical(self, p: Categorical):
        return random.choice(p.choices)


class RandomSearch(SearchAlgorithm):

    def __init__(self, search_space, experiments_factory):
        self.search_space = search_space
        self.experiments_factory = experiments_factory
        self.randomizer = Randomizer()

    @property
    def per_emit_count(self):
        warnings.warn('Per emit count not implemented.')
        return 1

    def ask(self) -> Optional[List[Experiment]]:

        try:
            return next(self._ask())
        except StopIteration:
            return None

    def _ask(self):

        while True:

            cfgs = []

            for _ in range(self.per_emit_count):

                cfg = dict()

                for p in self.search_space:
                    cfg[p.name] = p.accept(self.randomizer)

                prepared = self.experiments_factory.create(cfg)
                cfgs.append(prepared)

            yield cfgs

    def tell(self, experiment: Experiment):
        # no needed
        pass
