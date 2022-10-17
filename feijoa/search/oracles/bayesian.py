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
import logging
from typing import Generator, List, Optional

import numpy as np
from scipy.stats import norm

# noinspection PyUnresolvedReferences
# noinspection PyUnresolvedReferences
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor

from feijoa.models.configuration import Configuration
from feijoa.search.oracles.oracle import Oracle
from feijoa.search.visitors import Randomizer
from feijoa.utils.transformers import inverse_transform, transform

__all__ = ["Bayesian", "acquisition"]

log = logging.getLogger(__name__)


# noinspection PyPep8Naming
def acquisition(model, kind, X_samples, X, y, random_state=None, **kwargs):
    """
    Acquisition function for bayesian optimization.

    Args:
        model:
            Regressor model, must be fitted.
            Typically, Gaussian
        kind:
            Kind of acquisition function.
            Choices: ei, poi, ucb (only for GPR),
            lfboei, lfbopi, naive0 - model free.
        X_samples (numpy.ndarray):
            X samples to predict.
        X (numpy.ndarray):
            Features matrix.
        y (numpy.ndarray):
            Target values for X.
        random_state (int | None):
            Random state seed.

    Returns:
        Value of acquisition function.

    """

    if kind == "naive0":
        # experimental, research only
        return model.predict(X_samples)

    if kind == "lfboei":
        # https://arxiv.org/abs/2206.13035

        tau = np.quantile(y, q=0.33)
        classified = np.greater_equal(y, tau)
        x1, z1 = X[classified], classified[classified]
        x0, z0 = X, np.zeros_like(classified)
        w1 = (tau - y)[classified]
        w1 = w1 / np.mean(w1)
        w0 = 1 - z0

        x = np.concatenate([x1, x0], axis=0)
        z = np.concatenate([z1, z0], axis=0)

        s1 = x1.shape[0]
        s0 = x0.shape[0]

        # FIXME (qnbhd): ValueError: Input sample_weight contains NaN.
        w = np.concatenate(
            [w1 * (s1 + s0) / s1, w0 * (s1 + s0) / s0],
            axis=0,  # pragma: no mutate
        )
        w = w / np.mean(w)

        clf = RandomForestClassifier(
            n_jobs=-1, random_state=random_state
        )  # pragma: no mutate
        clf.fit(x, z, sample_weight=w)
        y_pred = clf.predict_proba(X_samples)[:, 1]
        return y_pred

    if kind == "lfbopoi":
        # https://arxiv.org/abs/2206.13035

        tau = np.quantile(y, q=0.33)
        classified = np.greater_equal(y, tau)
        clf = RandomForestClassifier(n_jobs=-1, random_state=random_state)
        clf.fit(X, classified)
        # FIXME (qnbhd): IndexError: index 1 is out of bounds for axis 1 with size 1
        y_pred = clf.predict_proba(X_samples)[:, 1]
        return y_pred

    assert isinstance(model, GaussianProcessRegressor), (
        "Model must be sklearn.GaussianProcessRegressor"
        "for classical ei, poi, ucb acquisition functions."
    )

    mean, std = model.predict(X_samples, return_std=True)
    best = min(mean)
    kappa = 2.5

    # regular acquisition functions.

    if kind == "poi":
        probs = norm.cdf((mean - best) / std)
        return probs

    elif kind == "ei":
        a = mean - best
        z = a / std
        return a * norm.cdf(z) + std * norm.pdf(z)

    elif kind == "ucb":
        return mean + kappa * std

    raise ValueError("Not correct acquisition function kind.")


class Bayesian(Oracle):
    """
    Bayesian optimization oracle.

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
        acq (str):
            Acquisition function.
            Can be `pi`, `ucb`, `ei` with Gaussian Regressor
            Or `naive0` - experimental, `lfboei`, `lfbopi`
        regr:
            Regression model, must have
                - fit(X, y)
                - predict_proba(X)
                - predict(X)
            methods. For example, you
            can use regressor from sklearn package
            (https://scikit-learn.org/)
        n_warmup (int):
            Warmup points count.

    .. note::
        `lfbopi` and `lfboei` taked from publication:
         https://arxiv.org/abs/2206.13035

    .. note::
        `naive0` - experimental function.

    """

    anchor = "bayesian"

    aliases = (
        "BayesianOracle",
        "bayesian",
        "bayes",
    )

    def __init__(
        self,
        search_space,
        *args,
        acq="ei",
        seed=0,
        regr="GaussianProcessRegressor",
        n_warmup=5,
        plugins=None,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)

        for p in plugins or []:
            # TODO (qnbhd): add task case with plugin.
            self.attach(p)

        self.search_space = search_space

        # build regression model

        # TODO (qnbhd): elliminate globals
        regr = globals()[regr]

        self.model = regr() if inspect.isclass(regr) else regr

        # take bounds

        self.bounds = search_space.bounds

        # trials pool for fitting

        self.X = np.empty(shape=(0, len(self.search_space)))

        # results pool for fitting

        self.y = np.empty(shape=(0,))

        # setup acquisition function

        if not isinstance(self.model, GaussianProcessRegressor):
            choices = ["lfboei", "lfbopoi", "naive0"]
            if acq in choices:
                self.acq_function = acq
            else:
                raise ValueError(
                    f"Acquisition function `{acq}` not"
                    f" available with `{regr}` regressor."
                )
        else:
            self.acq_function = acq

        log.critical(f"ACQ function: {self.acq_function}")

        # warmup points
        self.n_warmup = n_warmup

        # setup readable name
        self._name = f"Bayesian<{type(self.model).__name__}({self.acq_function})>"

        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        # TODO (qnbhd): add test case on configurations
        #  per emit count

        if not self._ask_gen:
            # build ask generator
            self._ask_gen = self._ask(n)

        return next(self._ask_gen)

    def _ask(self, n: int) -> Generator:
        """Main ask generator."""

        # make some warmup configurations

        randomizer = Randomizer(self.seed)
        random_samples = [
            Configuration(
                {p.name: p.accept(randomizer) for p in self.search_space},
                requestor=self.name,
            )
            for _ in range(self.n_warmup)
        ]

        yield random_samples

        self.model.fit(self.X, self.y)

        while True:
            x = self.opt_acquisition(n)
            configurations = list()
            for c in x:
                configurations.append(
                    Configuration(
                        transform(c, self.search_space),
                        requestor=self.name,
                    )
                )
            yield configurations
            self.model.fit(self.X, self.y)

    def opt_acquisition(self, n: int):
        """Optimize acquisition function."""

        n_samples = 100000

        X_samples = np.random.uniform(
            self.bounds[:, 0],
            self.bounds[:, 1],
            size=(n_samples, self.bounds.shape[0]),
        )

        scores = acquisition(
            self.model,
            self.acq_function,
            X_samples,
            self.X,
            self.y,
            random_state=self.seed,
        )

        assert len(scores) == n_samples

        minima_x = X_samples[scores.argsort()[:n]]

        return minima_x

    def tell(self, config, result):
        """Tell configuration's result."""

        vec = np.array(inverse_transform(config, self.search_space))

        self.X = np.concatenate([self.X, vec.reshape(1, -1)])  # pragma: no mutate
        self.y = np.concatenate([self.y, [result]])

        if len(self.y) > 5:  # pragma: no mutate
            self.notify("on_tell", config, result)

    def update(self, event, subject, *args, **kwargs):
        log.info(
            f"Event: {event}," f"Subject: {subject}" f"Args: {args}" f"Kwargs: {kwargs}"
        )
