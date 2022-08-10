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
"""Round robin meta oracle module."""

from collections import deque
import logging

from feijoa.search.oracles.meta.meta import MetaOracle
from feijoa.search.oracles.oracle import Oracle


log = logging.getLogger(__name__)

__all__ = ["RoundRobinMeta"]


class RoundRobinMeta(MetaOracle):
    """
    RoundRobin meta oracle.

    Raises:
        AnyError: If anything bad happens.

    """

    anchor = "roundrobin"
    aliases = ("roundrobin",)

    def __init__(self, *algorithms):
        super().__init__(*algorithms)
        self.oracle_deque = None

    @property
    def order(self):
        # noinspection PyUnresolvedReferences
        if not self.oracle_deque:
            self.oracle_deque = deque(self.oracles)

        self.oracle_deque.rotate(1)
        return self.oracle_deque

    def remove_oracle(self, oracle: Oracle):
        self.oracle_deque.remove(oracle)
        self.oracles.remove(oracle)
