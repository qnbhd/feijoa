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
"""Reducer class module."""

import logging

import numpy as np

from feijoa.plugins.plugin import Plugin
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import Real
from feijoa.search.space import SearchSpace


log = logging.getLogger(__name__)

__all__ = ["DomainReducer"]


class DomainReducer(Plugin):
    """
    A sequential domain reduction transformer bassed
    on the work by Stander, N. and Craig, K:
    "On the robustness of a simple domain reduction
    scheme for simulation‐based optimization"

    Link: http://www.truegrid.com/srsm_revised.pdf

    Based on: https://github.com/fmfn/BayesianOptimization

    Args:
        gamma_osc (float):
            Shrinkage parameter for oscillation.
            Typically, [0.5-0.7].
        gamma_pan (float):
            Panning parameter. Typically, 1.0.
        eta (float):
            Zoom parameter.

    Raises:
        AnyError: If anything bad happens.

    """

    anchor = "reducer"
    aliases = ("domain_reducer",)

    def __init__(
        self,
        gamma_osc: float = 0.7,
        gamma_pan: float = 1.2,
        eta: float = 0.9,
        min_window_value: float = 0.0,
        subscribers=None,
    ):

        super().__init__(subscribers=subscribers)

        self.gamma_osc = gamma_osc
        self.gamma_pan = gamma_pan
        self.eta = eta

        self.min_window_value = min_window_value
        self.min_window: np.ndarray = np.array([])

        self.bounds: np.ndarray = np.array([])
        self.original_bounds: np.ndarray = np.array([])

        self.previous_optimal: np.ndarray = np.array([])
        self.current_optimal: np.ndarray = np.array([])

        self.previous_d: np.ndarray = np.array([])
        self.current_d: np.ndarray = np.array([])

        self.c_hat: np.ndarray = np.array([])
        self.r: np.ndarray = np.array([])
        self.contraction_rate: np.ndarray = np.array([])
        self.c: np.ndarray = np.array([])
        self.gamma: np.ndarray = np.array([])

        self.fitted = False

    def init(self, space):
        """
        Init reducer.

        Args:
            space (SearchSpace):
                Search space instance.

        Raises:
            AnyError: If anything bad happens.

        """

        bounds = []

        for p in space:
            if isinstance(p, (Integer, Real)):
                bounds.append((p.low, p.high))
            if isinstance(p, Categorical):
                bounds.append((0, len(p.choices) - 1))

        self.original_bounds = np.array(bounds)
        self.bounds = np.array(np.copy(self.original_bounds))
        self.min_window = np.array(
            [self.min_window_value] * len(self.bounds)
        )

        self.previous_optimal = np.mean(self.bounds, axis=1)
        self.current_optimal = np.mean(self.bounds, axis=1)

        self.r = (
            self.original_bounds[:, 1] - self.original_bounds[:, 0]
        )

        self.current_d = (
            2.0
            * (self.current_optimal - self.previous_optimal)
            / self.r
        )
        self.previous_d = np.copy(self.current_d)

    # noinspection PyPep8Naming
    def refit(self, x_opt: np.ndarray):
        self.previous_optimal = self.current_optimal
        self.previous_d = x_opt

        self.current_d = (
            2.0
            * (self.current_optimal - self.previous_optimal)
            / self.r
        )

        self.c = self.current_d * self.previous_d

        self.c_hat = np.sqrt(np.abs(self.c)) * np.sign(self.c)

        self.gamma = 0.5 * (
            self.gamma_pan * (1.0 + self.c_hat)
            + self.gamma_osc * (1.0 - self.c_hat)
        )

        self.contraction_rate = self.eta + np.abs(self.current_d) * (
            self.gamma - self.eta
        )

        self.r = self.contraction_rate * self.r

    def _prune(
        self, new_bounds: np.ndarray, global_bounds: np.ndarray
    ) -> np.ndarray:
        Z = np.copy(new_bounds)
        Z[:, 1] = global_bounds[:, 0]
        Z.sort(axis=1)
        new_bounds[:, 0] = Z[:, 1]

        Z = np.copy(new_bounds)
        Z[:, 0] = global_bounds[:, 1]
        Z.sort(axis=1)
        new_bounds[:, 1] = Z[:, 0]
        new_bounds.sort(axis=1)

        for i, entry in enumerate(new_bounds):
            window_width = abs(entry[0] - entry[1])
            if window_width < self.min_window[i]:
                new_bounds[i, 0] -= (
                    self.min_window[i] - window_width
                ) / 2.0
                new_bounds[i, 1] += (
                    self.min_window[i] - window_width
                ) / 2.0

        return new_bounds

    def update(self, event, subject, *args, **kwargs):
        """Update reducer as subscriber to oracle."""

        if self.bounds.size == 0:
            self.init(subject.search_space)

        self.refit(subject.X[subject.y.argmin()])

        new_bounds = np.array(
            [
                self.current_optimal - 0.5 * self.r,
                self.current_optimal + 0.5 * self.r,
            ]
        ).T

        self.notify("on_suggest_search_space", new_bounds)
        self._prune(new_bounds, self.original_bounds)

        assert all(
            np.less(new_bounds[:, 0], new_bounds[:, 1])
        ), f"Incorrect bounds: {new_bounds}"

        self.bounds = np.concatenate([self.bounds, new_bounds])
        subject.bounds = new_bounds
