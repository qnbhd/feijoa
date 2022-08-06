# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Bayesian optimization module."""

import inspect
from typing import Generator
from typing import List
from typing import Optional

import numpy as np
from scipy.stats import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessRegressor

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.search.visitors import Randomizer


__all__ = ["BayesianAlgorithm"]


# noinspection PyPep8Naming
class BayesianAlgorithm(SearchAlgorithm):
    """Bayesian optimization algorithm.

    Bayesian optimization is a global optimization
    method for an unknown function (black box) with noise.
    Bayesian optimization applied to hyperparameters
    optimization builds a stochastic model of the mapping
    function from hyperparameter value to an objective
    function applied on the test set. By iteratively
    applying a perspective hyperparameter configuration
    based on the current model and then updating it,
    Bayesian optimization seeks to gather as much
    information as possible about that function and,
    in particular, the location of the optimum. The method
    attempts to balance probing (hyperparameters for which
    the change is least reliably known) and exploitation
    (hyperparameters that are expected to be closest to
    the optimum). In practice, Bayesian optimization
    has shown better results with less computation compared
    to grid search and random search due to the ability
    to judge the quality of experiments even before they
    are performed.

    Args:
        search_space (SearchSpace):
            Search space instance.
        acq_function (str):
            Acquisition function.
            Can be `pi`, `ucb`, `ei` with Gaussian Regressor
            Or `mc` - experimental, `lfboei`, `lfbopi`
        regressor:
            Regression model, must have
                - fit(X, y)
                - predict_proba(X)
                - predict(X)
            methods. For example, you
            can use regressor from sklearn package
            (https://scikit-learn.org/)

    .. note::
        `lfbopi` and `lfboei` taked from publication:
         https://arxiv.org/abs/2206.13035

    .. note::
        `mc` - experimental function.

    """

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

        # build regression model

        self.model = (
            regressor() if inspect.isclass(regressor) else regressor
        )

        # low and high bound of
        # target hyperparameters

        self.bounds = []

        for p in self.search_space:
            if isinstance(p, (Integer, Real)):
                self.bounds.append((p.low, p.high))
            if isinstance(p, Categorical):
                self.bounds.append((0, len(p.choices) - 1))

        self.bounds = np.array(self.bounds)

        # trials pool for fitting

        self.X = np.empty(shape=(0, len(self.search_space)))

        # results pool for fitting

        self.y = np.empty(shape=(0,))

        # setup random generator

        self.random_generator = np.random.RandomState(0)

        # setup acquisition function

        self.acq_function = (
            acq_function
            if isinstance(self.model, GaussianProcessRegressor)
            else "mc"
        )

        # setup readable name
        self._name = f"Bayesian<{type(self.model).__name__}({self.acq_function})>"

        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:

        if not self._ask_gen:
            # build ask generator
            self._ask_gen = self._ask(n)

        return next(self._ask_gen)

    def _to_feijoa_config(self, x):
        """Build feijoa-format
        configuration from vec x.

        Args:
            x (numpy.array):
                Input x vector for transformation.

        Returns:
            Feijoa-format configuration (dict).

        Raises:
            AnyError: If anything bad happens.

        """

        configuration = {}

        for p, v in zip(self.search_space, x):
            if isinstance(p, Real):
                configuration[p.name] = v

            # make math rounding

            rounded = int(v + (0.5 if v > 0 else -0.5))

            if isinstance(p, Integer):
                configuration[p.name] = rounded

            # pick up needed categorical value

            elif isinstance(p, Categorical):
                configuration[p.name] = p.choices[rounded]

        return configuration

    def _to_gp_config(self, cfg):
        """Build vec from Feijoa-format
        configuration.

        Args:
            cfg (dict | Configuration):
                Input configuration for transformation.

        Returns:
            Values vector (numpy.array).

        Raises:
            AnyError: If anything bad happens.

        """

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
        """Main ask generator."""

        # make some warmup configurations

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
                        self._to_feijoa_config(c), requestor=self.name
                    )
                )
            yield configurations
            self.model.fit(self.X, self.y)

    def acquisition(self, X_samples):
        """Acquisition function for bayesian optimization"""

        yhat = self.model.predict(self.X)
        best = min(yhat)

        if self.acq_function == "mc":
            # experimental, research only

            mean = self.model.predict(X_samples)
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

        # regular acquisition functions.

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
        """Optimize acquisition function."""

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
        """Tell configuration's result."""

        vec = np.array(self._to_gp_config(config))

        self.X = np.concatenate([self.X, vec.reshape(1, -1)])
        self.y = np.concatenate([self.y, [result]])
