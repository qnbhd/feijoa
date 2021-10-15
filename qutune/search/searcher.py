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
import json
import logging
import warnings
from collections import Coroutine

import hashlib
from numpy.ma import MaskedArray
import sklearn.utils.fixes

from qutune.search.renderer import Renderer
from utils.configurations import dump_config

sklearn.utils.fixes.MaskedArray = MaskedArray

from qutune.environment import Environment
from qutune.search.space import SearchSpace
from workloads.workload import Workload

import skopt

log = logging.getLogger(__name__)

class Searcher:

    def __init__(self, workload: Workload, space: SearchSpace):
        self.workload = workload
        self.space = space
        self.skopt_space = self.space.to_skopt()

        self.hashes_storage = dict()

        env = Environment()
        self.test_limit = env.test_limit
        self.test_count = 0

        self.opt = skopt.Optimizer(self.skopt_space)

        self.ask_coroutine = self._ask_coroutine()
        self.ask_coroutine.send(None)
        self.max_retries = 3

        self.renderer = Renderer()

    @staticmethod
    def hash(cfg):
        return \
            hashlib.sha1(json.dumps(cfg, sort_keys=True)
                .encode('utf-8')).hexdigest()

    def ask(self):
        try:
            # noinspection PyTypeChecker
            return next(self.ask_coroutine)
        except StopIteration:
            return None

    def _AskWrapper(self):
        @skopt.utils.use_named_args(self.skopt_space)
        def named(**kwargs):
            return kwargs

        cur_retries = 0
        while self.test_count < self.test_limit:
            cfg = self.opt.ask()

            named_cfg = named(cfg)
            h = self.hash(named_cfg)

            if h in self.hashes_storage:
                if cur_retries == 0:
                    log.warning(f'Current config'
                                f' {dump_config(named_cfg)} is measured before.')

                cur_retries += 1

                if cur_retries >= self.max_retries:
                    log.error('Technique does not generate new configurations')
                    break

                continue
            else:
                cur_retries = 0

            d = dict()
            for p, value in named_cfg.items():
                d[self.space.get_by_name(p)] = value

            yield d
            self.test_count += 1

    def _ask_coroutine(self) -> Coroutine:
        yield from self._AskWrapper()

    def tell(self, cfg, result):
        h = self.hash({
                p.name: v for p, v in cfg.items()})

        if h not in self.hashes_storage:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.opt.tell(list(cfg.values()), result)
                self.hashes_storage[h] = result


