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
import copy
import logging
from typing import Generator
from typing import List
from typing import Optional

from feijoa.models.configuration import Configuration
from feijoa.search.algorithms import SearchAlgorithm
from feijoa.search.parameters import Integer
from feijoa.search.space import SearchSpace
from feijoa.search.visitors import Randomizer


log = logging.getLogger(__name__)


class PatternSearch(SearchAlgorithm):
    """Pattern search implementation.

    The result can be used for functions that are
    not its continuous or differentiable. One such
    search method is "convergence" (see below), based
    on the theory of positive reasons. The optimization
    turns into the best match (the solution with the
    smallest error value) in the multidimensional
    analytical possibility space.

    See more: https://en.wikipedia.org/wiki/Pattern_search_(optimization)

    Implementation based on: https://github.com/jansel/opentuner/blob/master/opentuner/search/patternsearch.py

    Raises:
        AnyError: If anything bad happens.

    """

    anchor = "template"
    aliases = (
        "PatternSearch",
        "pattern",
        "patternsearch",
        "TemplateSearch",
        "templatesearch",
    )

    def __init__(self, search_space: SearchSpace, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_space = search_space
        self.step_size = 0.1
        self.results: List[tuple] = []
        self._ask_gen: Optional[Generator] = None

    def ask(self, n: int = 1) -> Optional[List[Configuration]]:
        if not self._ask_gen:
            log.debug(
                "Parameter `n` does not affect on configuration's count,"
                f" because {self.__class__.__name__} is sequential."
            )
            self._ask_gen = self._ask(n)
        return next(self._ask_gen)

    def _ask(self, n: int) -> Generator:
        randomizer = Randomizer()
        center = {
            p.name: p.accept(randomizer) for p in self.search_space
        }
        yield [Configuration(center, requestor=self.name)]

        def set_unit_value(p, config, uv):
            """Set unit value."""

            low, high = p.low, p.high

            if isinstance(p, Integer):
                low -= 0.4999
                high += 0.4999

            if low < high:
                val = uv * float(high - low) + low

                if isinstance(p, Integer):
                    val = round(val)

                val = max(low, min(val, high))
                config[p.name] = val

        while True:
            points = list()

            for param in self.search_space:
                if param.is_primitive():

                    unit_value = param.get_unit_value(
                        center[param.name]
                    )

                    if unit_value > 0.0:
                        down_cfg = copy.copy(center)
                        set_unit_value(
                            param,
                            down_cfg,
                            min(1.0, unit_value - self.step_size),
                        )
                        yield [
                            Configuration(
                                down_cfg, requestor=self.name
                            )
                        ]
                        points.append(down_cfg)

                    if unit_value < 1.0:
                        up_cfg = copy.copy(center)
                        set_unit_value(
                            param,
                            up_cfg,
                            min(1.0, unit_value + self.step_size),
                        )
                        yield [
                            Configuration(up_cfg, requestor=self.name)
                        ]
                        points.append(up_cfg)

                else:
                    cfg = copy.copy(center)
                    cfg[param.name] = param.accept(randomizer)
                    yield [Configuration(cfg, requestor=self.name)]
                    points.append(cfg)

            minima = min(self.results, key=lambda x: x[1])

            if minima[0] != center:
                center = copy.copy(minima[0])
            else:
                self.step_size /= 2.0

    def tell(self, config, result):
        self.results.append((config, result))
