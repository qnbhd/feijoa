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
import csv
import json
import logging
import os
from datetime import datetime
from multiprocessing import Pool
from os.path import abspath, dirname
from typing import Iterable, Callable

from rich.console import Console
from rich.markdown import Markdown
from rich import print_json
from polytune import __poly_folder__, __project_folder__

import polytune.environment as ENV
from polytune.convergence.plugin import ConvergencePlugin
from polytune.models.result import Result
from polytune.search.searcher import Searcher
from polytune.storages.storage import Storage


log = logging.getLogger(__name__)


class Runner:
    def __init__(self, searcher: Searcher,
                 storage: Storage,
                 metric_collector: Callable,
                 metrics: tuple,
                 objective: Callable):

        self.searcher = searcher
        self.metric_collector = metric_collector
        self.storage = storage
        self.objective = objective
        self.metrics = metrics

        self.tests_count = 0

        self.warmup_tests_count = ENV.test_limit // 5
        self.without_new_best = 0
        self.convergence_plugins = []

        self.console = Console()

    def add_convergence_plugin(self, plugin: ConvergencePlugin):
        self.convergence_plugins.append(plugin)

    def convergence_check(self) -> bool:
        if not self.tests_count >= self.warmup_tests_count:
            return False

        for plugin in self.convergence_plugins:
            if plugin.converged():
                log.info(plugin.reason)
                return True

        return self.tests_count >= ENV.test_limit

    def _process_wrapper(self) -> Iterable:

        while not self.convergence_check():

            suggested_cfgs = self.searcher.ask()

            if not suggested_cfgs:
                break

            with Pool(ENV.processes_count) as p:
                results = p.map(self.metric_collector, suggested_cfgs)

            results = map(Result.get, results)

            generated = list()

            for config, result in zip(suggested_cfgs, results):
                by_objective = self.objective(result)
                self.searcher.tell(config, by_objective)
                self.tests_count += 1
                generated.append(
                    (
                        list(config.data.keys()),
                        config,
                        result
                    )
                )

            yield from generated

    def process(self):
        log.info("Tuning session was started.")
        workload_args_list = "\n".join(
            [f"  * {k}: {v}" for k, v in ENV.workload_args.items()]
        )

        md = Markdown(f"""***
* Workload: {ENV.workload_name}
{workload_args_list}\n***""")

        self.console.print(md)

        # progress_wrapper = track(
        #     self._process_wrapper(),
        #     description="tests count",
        #     total=ENV.test_limit,
        #     # transient=True,
        #     update_period=0.01,
        # )

        for suggested, cfg, run_result in self._process_wrapper():
            self.storage.insert(cfg, run_result)
            best_config = self.storage.best_configuration(self.objective)
            best_result = self.storage.get_result(best_config)
            is_new_best = run_result == best_result

            if is_new_best:
                for plugin in self.convergence_plugins:
                    plugin.on_new_best_result(cfg, run_result)

                dumped = json.dumps(best_config.data, indent=2)
                log.info(f"[green]New best")
                log.info(dumped)
                log.info(f"With result: \n{best_result}")
                log.info(f"By objective: {self.objective(best_result)}")

                self.without_new_best = 0
            else:
                self.without_new_best += 1

        log.info("Tuning was finished.")

        workload_name = ENV.workload_name.replace("/", "_").replace(":", "").replace('__', '_')
        dt_string = datetime.now().strftime("%d-%m-%Y_%H:%M")
        output_filename = f"{workload_name}_{dt_string}.csv"
        dataframes_folder = os.path.join(__project_folder__, "tuning_dataframes")
        os.makedirs(dataframes_folder, exist_ok=True)

        cols = [
            'id', 'timestamp',
            *[f'metric_{k}' for k in self.metrics],
            *[f'param_{k}' for k in self.searcher.space.name2param.keys()]
        ]

        with open(os.path.join(dataframes_folder, output_filename), "w") as output_file:
            dict_writer = csv.DictWriter(
                output_file,
                fieldnames=cols,
                restval="-",
                delimiter=",",
            )
            dict_writer.writeheader()
            dict_writer.writerows(self.storage.results_list())

        log.info(f"Tuning dataframe was written in {output_filename}.")

        best_config = self.storage.best_configuration(self.objective)

        if best_config:
            md = Markdown(f"# Best configuration")
            self.console.print(md)
            self.console.print(
                f"[green][bold]{json.dumps(best_config.data, indent=2)}"
            )
