from typing import List, Optional

from polytune.models import Experiment
from polytune.search.algorithms import SearchAlgorithm


class SeedAlgorithm(SearchAlgorithm):

    def __init__(self, experiments_factory, *seeds):
        self.experiments_factory = experiments_factory
        self.seeds: list = list(seeds)
        self.is_emitted = False

    def add_seed(self, seed: dict):
        self.seeds.append(seed)

    def ask(self) -> Optional[List[Experiment]]:

        if not self.is_emitted:
            cfgs = [
                self.experiments_factory.create(seed)
                for seed in self.seeds
            ]
            self.is_emitted = True
            return cfgs
        else:
            return None

    def tell(self, experiment: Experiment):
        # Tell no needed
        pass

