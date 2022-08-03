import inspect
from typing import Generator
from typing import List
from typing import Optional
import warnings

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.search.visitors import Randomizer
import numpy as np
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessRegressor


# noinspection PyPep8Naming
class BayesianAlgorithm(SearchAlgorithm):

    anchor = "bayesian"
    aliases = (
        "BayesianAlgorithm",
        "bayesian",
        "bayes",
    )

    def __init__(
        self,
        search_space,
        *args,
        acq_function="ei",
        regressor=GaussianProcessRegressor,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.search_space = search_space
        self.model = (
            regressor() if inspect.isclass(regressor) else regressor
        )

        self.bounds = []

        for p in self.search_space:
            if isinstance(p, (Integer, Real)):
                self.bounds.append((p.low, p.high))
            if isinstance(p, Categorical):
                self.bounds.append((0, len(p.choices) - 1))

        self.bounds = np.array(self.bounds)

        self.X = np.empty(shape=(0, len(self.search_space)))
        self.y = np.empty(shape=(0,))
        self.random_generator = np.random.RandomState(0)
        self.n_warmup = 5
        self.acq_function = (
            acq_function
            if isinstance(self.model, GaussianProcessRegressor)
            else "mc"
        )
        self._name = f"Bayesian<{type(self.model).__name__}({self.acq_function})>"
        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            self._ask_gen = self._ask(n)
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

    def _ask(self, n: int) -> Generator:
        randomizer = Randomizer()
        random_samples = [
            Configuration(
                {
                    p.name: p.accept(randomizer)
                    for p in self.search_space
                },
                requestor=self.name,
            )
            for _ in range(n)
        ]

        yield random_samples

        self.model.fit(self.X, self.y)

        while True:
            x = self.opt_acquisition(n)
            configurations = list()
            for c in x:
                configurations.append(
                    Configuration(
                        self._to_gt_config(c), requestor=self.name
                    )
                )
            yield configurations
            self.model.fit(self.X, self.y)

    def acquisition(self, X_samples):
        yhat = self.model.predict(self.X)
        best = min(yhat)

        if self.acq_function == "mc":
            mean = self.model.predict(X_samples)
            warnings.warn(
                "Not correct acquisition function, research only"
            )
            negative = np.where(mean - best < 0)
            mean[negative] = 0
            return mean - best

        if self.acq_function == "lfboei":
            # https://arxiv.org/abs/2206.13035
            tau = np.quantile(self.y, q=0.33)
            classified = np.greater_equal(self.y, tau)
            x1, z1 = self.X[classified], classified[classified]
            x0, z0 = self.X, np.zeros_like(classified)
            w1 = (tau - self.y)[classified]
            w1 = w1 / np.mean(w1)
            w0 = 1 - z0
            x = np.concatenate([x1, x0], axis=0)
            z = np.concatenate([z1, z0], axis=0)
            s1 = x1.shape[0]
            s0 = x0.shape[0]
            w = np.concatenate(
                [w1 * (s1 + s0) / s1, w0 * (s1 + s0) / s0], axis=0
            )
            w = w / np.mean(w)

            clf = RandomForestClassifier(n_jobs=-1)
            clf.fit(x, z, sample_weight=w)
            y_pred = clf.predict_proba(X_samples)[:, 1]
            return y_pred

        if self.acq_function == "lfbopi":
            # https://arxiv.org/abs/2206.13035
            tau = np.quantile(self.y, q=0.33)
            classified = np.greater_equal(self.y, tau)
            clf = RandomForestClassifier(n_jobs=-1)
            clf.fit(self.X, classified)
            y_pred = clf.predict_proba(X_samples)[:, 1]
            return y_pred

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

    def opt_acquisition(self, n: int):
        n_warmup = 10000

        x_tries = self.random_generator.uniform(
            self.bounds[:, 0],
            self.bounds[:, 1],
            size=(n_warmup, self.bounds.shape[0]),
        )

        scores = self.acquisition(x_tries)
        minima_x = x_tries[scores.argsort()[:n]]

        return minima_x

    def tell(self, config, result):
        vec = np.array(self._to_gp_config(config))

        self.X = np.concatenate([self.X, vec.reshape(1, -1)])
        self.y = np.concatenate([self.y, [result]])
