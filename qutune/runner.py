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

from rich.console import Console
from rich.progress import track

from qutune.environment import Environment
from qutune.measurement.measurer import Measurer
from qutune.search.searcher import Searcher

log = logging.getLogger(__name__)

class Runner:

    def __init__(self, searcher: Searcher, measurer: Measurer):
        self.searcher = searcher
        self.measurer = measurer

        self.best_result = None
        self.best_config = None

    def _SearchWrapper(self):
        while True:
            try:
                cfg = self.searcher.ask()
                if not cfg:
                    break

                suggested = list(cfg.values())

                run_result = self.measurer.run_test(cfg)
                self.searcher.tell(suggested, run_result)
                yield suggested, cfg, run_result
            except KeyboardInterrupt:
                break


    def process(self):
        log.info('Tuning session was started.')

        ProgressWrapper = track(
            self._SearchWrapper(),
            description='tests count',
            total=Environment().test_limit,
            transient=True,
            update_period=0.01
        )

        for suggested, cfg, run_result in ProgressWrapper:
            if not self.best_result or run_result < self.best_result:
                self.best_result = run_result
                self.best_config = cfg
                log.info(f'New best'
                         f' \n{json.dumps({p.name: v for p, v in self.best_config.items()}, indent=2)}\n'
                         f'with result: \n{self.best_result}')

        log.info(f'Best cfg:'
                 f'\n{json.dumps({p.name: v for p, v in self.best_config.items()})} with result:\n{self.best_result}')


