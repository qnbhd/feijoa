from typing import List, Optional

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor

from gimeltune.models.experiment import Experiment
from gimeltune.search.algorithms import SearchAlgorithm
from gimeltune.search.parameters import Categorical, Integer, Real
from gimeltune.search.visitors import Randomizer


# noinspection PyPep8Naming
class BayesianAlgorithm(SearchAlgorithm):
    def __init__(self, search_space, experiments_factory, acq_function='ei', **kwargs):
        self.search_space = search_space
        self.experiments_factory = experiments_factory
        self._ask_gen = self._ask()
        self.model = GaussianProcessRegressor()

        self.bounds = []

        for p in self.search_space:
            if isinstance(p, (Integer, Real)):
                self.bounds.append((p.low, p.high))
            if isinstance(p, Categorical):
                self.bounds.append((0, len(p.choices) - 1))

        self.bounds = np.array(self.bounds)

        self.X = np.empty(shape=(0, len(self.search_space)))
        self.y = np.empty(shape=(0, ))
        self.random_generator = np.random.RandomState(0)
        self.n_warmup = 5

        self.acq_function = acq_function

    def ask(self) -> Optional[List[Experiment]]:
        return next(self._ask_gen)

    def _to_gt_config(self, x):
        configuration = {}

        for p, v in zip(self.search_space, x):
            if isinstance(p, Real):
                configuration[p.name] = v

            rounded = int(v + (0.5 if v > 0 else -0.5))

            if isinstance(p, Integer):
                configuration[p.name] = rounded
            elif isinstance(p, Categorical):
                configuration[p.name] = p.choices[rounded]

        return configuration

    def _to_gp_config(self, cfg):
        vec = []

        for p_name, v in cfg.items():
            p = self.search_space.get(p_name)

            if isinstance(p, (Integer, Real)):
                vec.append(v)
            if isinstance(p, Categorical):
                index = p.choices.index(v)
                vec.append(index)

        return vec

    def _ask(self):

        randomizer = Randomizer()
        random_samples = [
            self.experiments_factory.create(
                {p.name: p.accept(randomizer)
                 for p in self.search_space}) for _ in range(self.n_warmup)
        ]

        yield random_samples

        while True:
            x = self.opt_acquisition()
            cfg = self._to_gt_config(x)
            yield [self.experiments_factory.create(cfg)]
            self.model.fit(self.X, self.y)

    def surrogate(self, X):
        return self.model.predict(X, return_std=True)

    def acquisition(self, X_samples):
        mean, std = self.surrogate(X_samples)
        yhat, _ = self.surrogate(self.X)
        best = min(yhat)
        kappa = 2.5

        if self.acq_function == "poi":
            probs = norm.cdf((mean - best) / (std + 1e-9))
            return probs
        elif self.acq_function == "ei":
            a = mean - best
            z = a / std
            return a * norm.cdf(z) + std * norm.pdf(z)
        elif self.acq_function == "ucb":
            return mean + kappa * std

    def opt_acquisition(self):
        n_warmup = 10000

        x_tries = self.random_generator.uniform(self.bounds[:, 0],
                                                self.bounds[:, 1],
                                                size=(n_warmup,
                                                      self.bounds.shape[0]))

        scores = self.acquisition(x_tries)
        minima_x = x_tries[scores.argmin()]

        return minima_x

    def tell(self, experiment: Experiment):
        vec = np.array(self._to_gp_config(experiment.params))

        self.X = np.concatenate([self.X, vec.reshape(1, -1)])
        self.y = np.concatenate([self.y, [experiment.objective_result]])
