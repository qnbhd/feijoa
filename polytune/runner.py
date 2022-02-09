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
from datetime import datetime
from functools import partial
from itertools import repeat

import csv

import numpy
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track

import polytune.environment as ENV
from polytune.measurement.measurer import Measurer
from polytune.search.searcher import Searcher
from rich.table import Table

from multiprocessing import Pool

log = logging.getLogger(__name__)


def f(config, measurer):
    return measurer.run_test(config)


class Runner:

    def __init__(self, searcher: Searcher, measurer: Measurer):
        self.searcher = searcher
        self.measurer = measurer

        self.best_result = None
        self.best_config = None
        self.tests_count = 0

        self.impacts_history = numpy.array([])
        self.warmup_tests_count = ENV.test_limit // 5
        self.impact_threshold = 0.005
        self.without_new_best = 0
        self.without_new_best_threshold = ENV.test_limit // 5

        self.console = Console()

    def convergence_check(self):
        test_check = self.tests_count >= ENV.test_limit

        warmup_stage_is_completed = self.tests_count >= self.warmup_tests_count
        if warmup_stage_is_completed:
            chunk_mean = self.impacts_history[len(self.impacts_history)//2:].mean()

            if chunk_mean < self.impact_threshold:
                log.info(f'Small impact in last {len(self.impacts_history)} best results.')
                return True
            if self.without_new_best > self.without_new_best_threshold:
                log.info(f'No new best results in last {self.without_new_best} tests.')
                return True

        return test_check

    @property
    def workload(self):
        return self.searcher.workload

    def _SearchWrapper(self):
        while not self.convergence_check() and (suggested_cfgs := self.searcher.ask()):
            try:

                with Pool(ENV.processes_count) as p:
                    results = p.starmap(f, zip(suggested_cfgs, repeat(self.measurer)))

                for config, result in zip(suggested_cfgs, results):
                    self.searcher.tell(config, result)
                    self.tests_count += 1

                generated = [
                    (list(c.keys()), c, result)
                    for c, result in zip(suggested_cfgs, results)
                ]

                yield from generated
            except KeyboardInterrupt:
                break

    def print_header(self):
        log.info('Tuning session was started.')
        workload_args_list = '\n'.join([f'  * {k}: {v}' for k, v in ENV.workload_args.items()])

        md = Markdown(f"""***
* Workload: {ENV.workload_name}
{workload_args_list}\n***""")

        self.console.print(md)

    def process(self):
        self.print_header()

        ProgressWrapper = track(
            self._SearchWrapper(),
            description='tests count',
            total=ENV.test_limit,
            transient=True,
            update_period=0.01
        )

        results = []

        for suggested, cfg, run_result in ProgressWrapper:
            results.append(
                {'id': len(results),
                 'result': run_result,
                 **{p.name: v for p, v in cfg.items()}})

            if not self.best_result or run_result < self.best_result:
                if self.best_result:
                    imp = (self.best_result - run_result) / run_result
                    self.impacts_history = numpy.append(self.impacts_history, imp)

                self.best_result = run_result
                self.best_config = cfg

                dumped = self.workload.render(self.best_config)
                log.info(f'[green]New best:\n{dumped}\n\nwith result: \n{self.best_result}')

                self.without_new_best = 0
            else:
                self.without_new_best += 1

        log.info('Tuning was finished.')

        workload_name = ENV.workload_name.replace('/', '_').replace(':', '')
        dt_string = datetime.now().strftime("%d-%m-%Y_%H:%M")
        output_filename = f'{workload_name}_{dt_string}.csv'
        dataframes_folder = os.path.join(os.getcwd(), 'tuning_dataframes')
        os.makedirs(dataframes_folder, exist_ok=True)

        with open(os.path.join(dataframes_folder, output_filename), 'w') as output_file:
            dict_writer = csv.DictWriter(
                output_file, fieldnames=['id', 'result', *self.searcher.space.name2param.keys()],
                restval='-', delimiter=',')
            dict_writer.writeheader()
            dict_writer.writerows(results)

        log.info(f'Tuning dataframe was written in {output_filename}.')

        if self.best_config:
            md = Markdown(f'# Best configuration')
            self.console.print(md)
            self.console.print(f'[green][bold]{self.workload.render(self.best_config)}')



