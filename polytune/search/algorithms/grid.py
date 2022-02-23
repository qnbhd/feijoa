import warnings
from itertools import product
from typing import List, Optional

import numpy

from polytune.models.experiment import Experiment
from polytune.search.algorithms import SearchAlgorithm
from polytune.search.parameters import (Categorical, Integer,
                                        ParametersVisitor, Real)

__all__ = [
    'GridSearch'
]


class GridMaker(ParametersVisitor):
    """

    """

    EPS = 0.1

    def visit_integer(self, p: Integer):
        return range(p.low, p.high)

    def visit_real(self, p: Real):
        return numpy.arange(p.low, p.high + GridMaker.EPS, GridMaker.EPS)

    def visit_categorical(self, p: Categorical):
        return p.choices


class GridSearch(SearchAlgorithm):

    def __init__(self, search_space, experiments_factory):
        self.search_space = search_space
        self.experiments_factory = experiments_factory

        grids = [
            p.accept(GridMaker())
            for p in self.search_space.params
        ]

        self.prod_iter = product(*grids)

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

            for i in range(self.per_emit_count):
                try:
                    generation = next(self.prod_iter)
                except StopIteration:
                    break

                cfg = {
                    h.name: v
                    for h, v in zip(self.search_space, generation)
                }

                cfgs.append(self.experiments_factory.create(cfg))

            if not cfgs:
                yield None

            yield cfgs

    def tell(self, experiment: Experiment):
        # no needed
        pass
