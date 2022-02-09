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
import logging
import warnings
from collections import Coroutine

from polytune.models.configuration import Configuration
from polytune.search.algorithms.skopt import SkoptBayesianAlgorithm
from polytune.storages import Storage

import polytune.environment as ENV

from polytune.search.space import SearchSpace
from workloads.workload import Workload


log = logging.getLogger(__name__)


class Searcher:

    def __init__(self, workload: Workload, space: SearchSpace, storage: Storage):
        self.workload = workload
        self.space = space
        self.storage = storage

        self.search_algorithm = SkoptBayesianAlgorithm(space)

        self.test_limit = ENV.test_limit
        self.test_count = 0
        self.max_retries = 3

        self.ask_coroutine = self._ask_coroutine()
        self.ask_coroutine.send(None)

    def ask(self):
        try:
            # noinspection PyTypeChecker
            return next(self.ask_coroutine)
        except StopIteration:
            return None

    def _ask_coroutine(self) -> Coroutine:
        retries = 0
        while retries != self.max_retries:
            suggested_configs_list = self.search_algorithm.ask()

            to_emit = list()

            for c in suggested_configs_list:
                h = c.get_hash()

                if self.storage.hash_is_exists(h):
                    retries += 1
                    continue
                else:
                    retries = 0

                to_emit.append(c)

            yield to_emit

    def tell(self, cfg: Configuration, result):
        h = cfg.get_hash()

        if not self.storage.hash_is_exists(h):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.search_algorithm.tell(cfg, result)
                self.storage.insert_hash(h)


