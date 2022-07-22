from typing import List, Optional, Generator

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor

from gimeltune.models.configuration import Configuration
from gimeltune.models.experiment import Experiment
from gimeltune.search.algorithms import SearchAlgorithm
from gimeltune.search.parameters import Categorical, Integer, Real
from gimeltune.search.visitors import Randomizer


# noinspection PyPep8Naming
class BayesianAlgorithm(SearchAlgorithm):

    def __init__(self,
        search_space,
        *args,
        acq_function='ei',
        regressor=GaussianProcessRegressor,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.search_space = search_space
        self._ask_gen = self._ask()
        self.model = regressor()

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
        self._name = f'Bayesian<{regressor.__name__}>'

        self.acq_function = acq_function

    def ask(self) -> Optional[List[Configuration]]:
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

    def _ask(self) -> Generator:
        randomizer = Randomizer()
        random_samples = [
            Configuration(
                {
                    p.name: p.accept(randomizer) for p in self.search_space
                },
                requestor=self.name
            )
            for _ in range(self.n_warmup)
        ]

        yield random_samples

        self.model.fit(self.X, self.y)

        while True:
            x = self.opt_acquisition()
            cfg = self._to_gt_config(x)
            yield [Configuration(cfg, requestor=self.name)]
            self.model.fit(self.X, self.y)

    def acquisition(self, X_samples):
        yhat = self.model.predict(self.X)
        best = min(yhat)

        if not isinstance(self.model, GaussianProcessRegressor):
            return np.array([
                max(0, best - y) for y in yhat
            ])

        mean, std = self.model.predict(X_samples, return_std=True)
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

    def tell(self, config, result):
        vec = np.array(self._to_gp_config(config))

        self.X = np.concatenate([self.X, vec.reshape(1, -1)])
        self.y = np.concatenate([self.y, [result]])
