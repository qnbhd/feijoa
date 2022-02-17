from typing import Optional, List

from polytune.search.algorithms import SearchAlgorithm
from polytune.models import Experiment


class SeedAlgorithm(SearchAlgorithm):

    def __init__(self, experiments_factory, *seeds):
        self.experiments_factory = experiments_factory
        self.seeds: list = list(seeds)
        self.is_measured = False

    def add_seed(self, seed: dict):
        self.seeds.append(seed)

    def ask(self) -> Optional[List[Experiment]]:

        if not self.is_measured:
            cfgs = [
                self.experiments_factory.create(seed)
                for seed in self.seeds
            ]

            return cfgs
        else:
            return None

    def tell(self, experiment: Experiment):
        # Tell no needed
        pass

