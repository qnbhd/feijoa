# MIT License
#
# Copyright (c) 2021 Templin Konstantin
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
import warnings
from typing import List, Optional

from gimeltune.models.experiment import Experiment
from gimeltune.search.algorithms import SearchAlgorithm
from gimeltune.search.visitors import Randomizer

__all__ = ["RandomSearch"]


class RandomSearch(SearchAlgorithm):
    def __init__(self, search_space, experiments_factory, **kwargs):
        self.search_space = search_space
        self.experiments_factory = experiments_factory
        self.randomizer = Randomizer()
        self._ask_gen = self._ask()

    @property
    def per_emit_count(self):
        warnings.warn("Per emit count not implemented.")
        return 1

    def ask(self) -> Optional[List[Experiment]]:
        return next(self._ask_gen)

    def _ask(self):

        while True:

            cfgs = []

            for _ in range(self.per_emit_count):

                cfg = dict()

                for p in self.search_space:
                    cfg[p.name] = p.accept(self.randomizer)

                prepared = self.experiments_factory.create(cfg)
                cfgs.append(prepared)

            yield cfgs

    def tell(self, experiment: Experiment):
        # no needed
        pass
