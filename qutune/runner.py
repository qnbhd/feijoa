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

import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track

from qutune.environment import Environment
from qutune.measurement.measurer import Measurer
from qutune.search.searcher import Searcher
from utils.configurations import dump_config

log = logging.getLogger(__name__)

class Runner:

    def __init__(self, searcher: Searcher, measurer: Measurer):
        self.searcher = searcher
        self.measurer = measurer

        self.best_result = None
        self.best_config = None

    @property
    def workload(self):
        return self.searcher.workload

    def _SearchWrapper(self):
        while True:
            try:
                cfg = self.searcher.ask()
                if not cfg:
                    break

                suggested = list(cfg.values())

                run_result = self.measurer.run_test(cfg)
                self.searcher.tell(cfg, run_result)
                yield suggested, cfg, run_result
            except KeyboardInterrupt:
                break


    def process(self):

        log.info('Tuning session was started.')

        env = Environment()

        workload_args_list = '\n'.join([f'  * {k}: {v}' for k, v in env.workload_args.items()])

        md = Markdown(f"""***
* Workload: {env.workload_name}
{workload_args_list}\n***""")
        console = Console()
        console.print(md)

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
                dumped = self.workload.render(self.best_config)
                log.info(f'[green]New best:\n{dumped}\n'
                         f'\nwith result: \n{self.best_result}')

        log.info('Tuning was finished.')

        if self.best_config:
            md = Markdown(f'# Best configuration')
            console.print(md)
            console.print(f'[green][bold]{self.workload.render(self.best_config)}')


