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
from typing import List, Optional

from gimeltune.models import Experiment
from gimeltune.search.algorithms import SearchAlgorithm


class SeedAlgorithm(SearchAlgorithm):

    def __init__(self, experiments_factory, *seeds):
        self.experiments_factory = experiments_factory
        self.seeds: list = list(seeds)
        self.is_emitted = False

    def add_seed(self, seed: dict):
        self.seeds.append(seed)

    def ask(self) -> Optional[List[Experiment]]:

        if not self.is_emitted:
            cfgs = [
                self.experiments_factory.create(seed)
                for seed in self.seeds
            ]
            self.is_emitted = True
            return cfgs
        else:
            return None

    def tell(self, experiment: Experiment):
        # Tell no needed
        pass

