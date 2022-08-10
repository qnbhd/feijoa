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
"""Meta oracle base class module."""

import abc
import logging
from typing import Generator
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration
from feijoa.search.oracles.oracle import Oracle
from feijoa.utils.imports import LazyModuleImportProxy


seed = LazyModuleImportProxy("feijoa.search.seed")


log = logging.getLogger(__name__)


class MetaOracle(Oracle):
    """
    Meta-search oracle.

    Used for pick up oracles.

    Raises:
        AnyError: If anything bad happens.

    """

    def __init__(self, *oracles, **kwargs):
        super().__init__(*oracles, **kwargs)
        self.oracles = list(oracles)
        self.ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self.ask_gen:
            self.ask_gen = self._ask(n)
        return next(self.ask_gen)

    def _ask(self, n: int) -> Generator:
        prev_picked = ""

        # pick up all seed's oracles

        seed_oracles = [
            a for a in self.oracles if isinstance(a, seed.SeedOracle)
        ]

        # remove all seed's oracles

        for oracle in seed_oracles:
            self.remove_oracle(oracle)

        if seed_oracles:
            log.debug("Let's measure seed configurations!")
            for oracle in seed_oracles:
                configs = oracle.ask(n)
                yield configs

        while True:
            for oracle in self.order:
                if not prev_picked or prev_picked != oracle.name:
                    log.debug(f"Pick {oracle.name}")
                configs = oracle.ask(n)
                yield configs
                prev_picked = oracle.name

    def tell(self, config, result):
        """
        Tell results to all search oracles"""

        for oracle in self.oracles:
            oracle.tell(config, result)

    def add_oracle(self, oracle: Oracle):
        """
        Append oracle to oracles list.

        Args:
            oracle (Oracle):
                search oracle instance.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

        self.oracles.append(oracle)

    @abc.abstractmethod
    def remove_oracle(self, oracle: Oracle):
        """
        Remove oracle from inner oracles
        pool in meta-oracle.

        Args:
            oracle (Oracle):
                search oracle instance.

        Returns:
            None

        Raises:
            AnyError: If anything bad happens.

        """

    @property
    @abc.abstractmethod
    def order(self):
        """Get order for oracles."""

        raise NotImplementedError()
