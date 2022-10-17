import logging
import math
import sys
from typing import Generator, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal

from feijoa.models.configuration import Configuration
from feijoa.search.oracles.oracle import Oracle
from feijoa.utils.transformers import transform


# noinspection PyAbstractClass,SpellCheckingInspection,PyPep8Naming
class BCMAES(Oracle):

    anchor: str = "BCMAES"
    aliases: Tuple = ("bcmaes", "BCMAES", "bCMAES")

    def __init__(self, search_space, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.list_x_star = list()
        self.list_fx_star = list()

        self.space = search_space
        self.bounds = self.space.bounds

        # TODO (qnbhd): change to
        # n = 4 + int(3 * math.log(len(mu_0)))

        self.mu0 = np.random.uniform(
            self.bounds[:, 0],
            self.bounds[:, 1],
            size=(self.bounds.shape[0],),
        )

        self.tol = 0.005

        self.n = 4 + int(3 * math.log(len(self.mu0)))
        self.k0 = 4
        self.v0 = self.n + 2
        self.factor = 1
        self.psi = np.eye(2)
        self.x_star_min = self.mu0
        self.var_star_min = self.psi
        self.fx_star_min = sys.float_info.max
        self.count = 0
        self.step = 0

        self.variance = np.ones([self.n, self.n])
        self.results = []

        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        # TODO (qnbhd): add test case on configurations
        #  per emit count

        if not self._ask_gen:
            # build ask generator
            self._ask_gen = self._ask(n)

        return next(self._ask_gen)

    # noinspection PyUnusedLocal
    def _ask(self, W: int) -> Generator:
        while True:
            # while np.linalg.norm(self.variance) > self.tol:
            E_mu = self.mu0
            E_sigma = self.psi / (self.v0 - self.n - 1)
            self.step += 1

            # FIXME (qnbhd): ValueError: mean and cov must have same length
            sample_X = np.random.multivariate_normal(
                mean=E_mu, cov=E_sigma, size=(self.n,)
            )
            sample_X = np.clip(sample_X, self.bounds[:, 0], self.bounds[:, 1])

            yield self.make_configs(sample_X)

            # TODO (qnbhd): FIX
            g_x = self.results.pop()

            df = pd.DataFrame(sample_X)
            df["g_x"] = g_x
            df["g_x"] = g_x
            df["d"] = multivariate_normal.pdf(
                sample_X, mean=E_mu, cov=E_sigma, allow_singular=True
            )
            x_order_d = df.sort_values(by=["d"], ascending=False)
            x_order_f = x_order_d.sort_values(by=["g_x"], kind="mergesort")

            d_ordered = x_order_d[x_order_d.columns[-1:]].values / sum(df["d"])
            x_order_f = x_order_f[x_order_f.columns[:-2]].values
            x_order_d = x_order_d[x_order_d.columns[:-2]].values

            x_all = df[df.columns[:-2]].values
            d = np.array(df["d"])[:, None] / sum(df["d"])
            x_bar_f = np.sum(x_order_f * d_ordered, axis=0)
            x_bar = np.sum(x_all * d, axis=0)
            mean = x_order_f[0]

            # sigma part :
            sigma_emp = np.dot((x_all - x_bar).T, (x_all - x_bar) * d)
            sigma_ordered = np.dot(
                (x_order_f - x_bar_f).T,
                (x_order_f - x_bar_f) * d_ordered,
            )
            # other :
            self.variance = (sigma_ordered - (sigma_emp - E_sigma)) * self.factor

            variance_norm = np.linalg.norm(self.variance)

            # TODO (qnbhd): FIX
            yield self.make_configs([mean])

            fx_star = self.results.pop()

            if fx_star < self.fx_star_min:
                # if self.fx_star_min - fx_star < 1e-5:
                #     return list_x_star, list_fx_star
                self.count = 0
                self.factor = 1
                self.fx_star_min = fx_star
                self.x_star_min = mean
                if variance_norm < 100 * self.n:
                    self.var_star_min = self.variance
                self.list_x_star.append(mean)

                yield self.make_configs([mean])

                # TODO (qnbhd): FIX
                self.list_fx_star.append(self.results.pop())
            else:
                self.list_x_star.append(self.x_star_min)
                # TODO (qnbhd): FIX
                yield self.make_configs([self.x_star_min])
                self.list_fx_star.append(self.results.pop())

                self.count += 1

                if variance_norm > 100 * self.n:
                    mean = self.x_star_min
                    self.variance = self.var_star_min
                    self.mu0 = mean

                if self.count > 5:
                    self.factor = 1.5
                if self.count == 20:
                    mean = self.x_star_min
                    self.variance = self.var_star_min
                    self.mu0 = mean
                if self.count > 20:
                    self.factor = 0.9
                if self.count > 30:
                    self.factor = 0.7
                if self.count > 40:
                    self.factor = 0.5

            self.mu0 = (self.mu0 * self.k0 + self.n * mean) / (self.k0 + self.n)
            self.k0 = self.k0 + self.n
            self.v0 = self.v0 + self.n
            self.psi = (
                self.psi
                + (self.k0 * self.n)
                / (self.k0 + self.n)
                * np.dot(np.mat(mean - self.mu0), np.mat(mean - self.mu0).T)
                + self.variance * (self.n - 1)
            )
            self.psi = self.psi * self.factor

    def tell(self, config, result):
        self.results.append(result)

    def make_configs(self, sample):
        configurations = list()
        for c in sample:
            configurations.append(
                Configuration(
                    # transform(np.clip(c, self.bounds[:, 0], self.bounds[:, 1]), self.space),
                    transform(c, self.space),
                    requestor=self.name,
                )
            )
        return configurations
