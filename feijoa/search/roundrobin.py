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
from collections import deque
import logging

from feijoa.search.algorithms.algorithm import SearchAlgorithm
from feijoa.search.meta import MetaSearchAlgorithm


log = logging.getLogger(__name__)

__all__ = ["RoundRobinMeta"]


class RoundRobinMeta(MetaSearchAlgorithm):
    """
    Experiment's optimizer class.

    Optimizer has two main methods:

    Parameters:
        - space
        - experiments_factory
    """

    anchor = "roundrobin"
    aliases = ("roundrobin",)

    def __init__(self, *algorithms):
        super().__init__(*algorithms)
        self.algo_deq = None

    @property
    def order(self):
        # noinspection PyUnresolvedReferences
        if not self.algo_deq:
            self.algo_deq = deque(self.algorithms)

        self.algo_deq.rotate(1)
        return self.algo_deq

    def remove_algorithm(self, algo: SearchAlgorithm):
        self.algo_deq.remove(algo)
        self.algorithms.remove(algo)
