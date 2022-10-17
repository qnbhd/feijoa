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
"""Grid search class module."""

from itertools import product
import logging
from typing import Generator
from typing import List
from typing import Optional

import numpy
import optuna

from feijoa.models.configuration import Configuration
from feijoa.search.oracles.oracle import Oracle
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import ParametersVisitor
from feijoa.search.parameters import Real


__all__ = ["OptunaTPE"]

log = logging.getLogger(__name__)


class OptunaTPE(Oracle):

    SAMPLER = optuna.samplers.TPESampler

    anchor = "optuna_tpe"
    aliases = (
        "Optuna-TPE",
        "OPTUNA-TPE",
    )

    def __init__(self, search_space, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space = search_space
        self._ask_gen = None
        self.name = f"Optuna<{self.SAMPLER.__name__}>"
        self.study = optuna.create_study(
            sampler=self.SAMPLER(seed=self.seed)
        )
        self.trial = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            self._ask_gen = self._ask(n)
        return next(self._ask_gen)

    def _ask(self, n: int) -> Generator:
        while True:
            self.trial = self.study.ask()
            configuration = {}

            for param in self.space:
                if isinstance(param, Real):
                    configuration[
                        param.name
                    ] = self.trial.suggest_float(
                        param.name, low=param.low, high=param.high
                    )
                elif isinstance(param, Integer):
                    configuration[
                        param.name
                    ] = self.trial.suggest_int(
                        param.name, low=param.low, high=param.high
                    )
                elif isinstance(param, Categorical):
                    configuration[
                        param.name
                    ] = self.trial.suggest_categorical(
                        param.name, choices=param.choices
                    )

            c = Configuration(configuration, requestor=self.name)
            yield [c]

    def tell(self, config, result):
        """No needed."""
        log.info(f"Telled for {self.name}")
        self.study.tell(self.trial, result)


class OptunaCMAES(OptunaTPE):
    anchor = "optuna_cmaes"
    aliases = ("optuna-cmaes", "Optuna-CMAES")
    SAMPLER = optuna.samplers.CmaEsSampler  # type: ignore


class OptunaNSGAII(OptunaTPE):
    anchor = "optuna_nsgaii"
    aliases = ("optuna-nsgaii", "Optuna-NSGAII")
    SAMPLER = optuna.samplers.NSGAIISampler  # type: ignore


class OptunaMOTPE(OptunaTPE):
    anchor = "optuna_motpe"
    aliases = ("optuna-motpe", "Optuna-MOTPE")
    SAMPLER = optuna.samplers.MOTPESampler  # type: ignore
