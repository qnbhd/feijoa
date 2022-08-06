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

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Categorical
from feijoa.search.parameters import Integer
from feijoa.search.parameters import ParametersVisitor
from feijoa.search.parameters import Real


__all__ = ["GridSearch"]

log = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
class GridMaker(ParametersVisitor):
    """Simple grid creation for different parameters.

    Args:
        EPS (float):
            Sample rate for included-valued parameters

    Raises:
        AnyError: If anything bad happens.

    """

    EPS = 0.1

    def visit_integer(self, p: Integer):
        """Pick up integer grid."""

        return range(p.low, p.high + 1)

    def visit_real(self, p: Real):
        """Pick up real grid."""

        return numpy.round(
            numpy.arange(
                p.low, p.high + GridMaker.EPS, GridMaker.EPS
            ),
            2,
        )

    def visit_categorical(self, p: Categorical):
        """Pick up categorical grid."""

        return p.choices


class GridSearch(SearchAlgorithm):
    """Simple grid search.

    Makes a full iteration over a manually
    specified subset of hyperparameter spaces
    of the algorithm.

    Raises:
        AnyError: If anything bad happens.

    """

    anchor = "grid"
    aliases = (
        "GridSearch",
        "grid",
    )

    def __init__(self, search_space, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_space = search_space

        # grids for all parameters

        grids = [
            p.accept(GridMaker()) for p in self.search_space.params
        ]

        # iterator for grid search

        self.prod_iter = product(*grids)

        self._ask_gen = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            self._ask_gen = self._ask(n)
        return next(self._ask_gen)

    def _ask(self, n: int) -> Generator:

        while True:
            cfgs = []

            for _ in range(n):
                try:
                    generation = next(self.prod_iter)
                except StopIteration:
                    break

                cfg = {
                    h.name: v
                    for h, v in zip(self.search_space, generation)
                }

                cfgs.append(Configuration(cfg, requestor=self.name))

            if not cfgs:
                yield None

            yield cfgs

    def tell(self, config, result):
        """No needed."""

        pass
