import copy
from typing import List, Optional

from gimeltune.models import Experiment, ExperimentsFactory
from gimeltune.search.algorithms import SearchAlgorithm
from gimeltune.search.parameters import Integer
from gimeltune.search.space import SearchSpace
from gimeltune.search.visitors import Randomizer


class TemplateSearchAlgorithm(SearchAlgorithm):
    def __init__(self, search_space: SearchSpace,
                 experiments_factory: ExperimentsFactory, **kwargs):
        self.search_space = search_space
        self.experiments_factory = experiments_factory
        self.step_size = 0.1
        self._ask_gen = self._ask()
        self.results = []

    def ask(self) -> Optional[List[Experiment]]:
        return next(self._ask_gen)

    def _ask(self):

        randomizer = Randomizer()

        center = {p.name: p.accept(randomizer) for p in self.search_space}

        yield [self.experiments_factory.create(center)]

        def set_unit_value(p, config, uv):
            low, high = p.low, p.high

            if isinstance(p, Integer):
                low -= 0.4999
                high += 0.4999

            if low < high:
                val = uv * float(high - low) + low

                if isinstance(p, Integer):
                    val = round(val)

                val = max(low, min(val, high))
                config[p.name] = val

        while True:
            points = list()

            for param in self.search_space:
                if param.is_primitive():

                    unit_value = param.get_unit_value(center[param.name])

                    if unit_value > 0.0:
                        down_cfg = copy.copy(center)
                        set_unit_value(param, down_cfg,
                                       min(1.0, unit_value - self.step_size))
                        yield [self.experiments_factory.create(down_cfg)]
                        points.append(down_cfg)

                    if unit_value < 1.0:
                        up_cfg = copy.copy(center)
                        set_unit_value(param, up_cfg,
                                       min(1.0, unit_value + self.step_size))
                        yield [self.experiments_factory.create(up_cfg)]
                        points.append(up_cfg)

                else:
                    cfg = copy.copy(center)
                    cfg[param.name] = param.accept(randomizer)
                    yield [self.experiments_factory.create(cfg)]
                    points.append(cfg)

            minima = min(self.results, key=lambda x: x[1])

            if minima[0] != center:
                center = copy.copy(minima[0])
            else:
                self.step_size /= 2.0

    def tell(self, experiment: Experiment):
        self.results.append((experiment.params, experiment.objective_result))
