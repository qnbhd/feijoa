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
import logging
import os
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool
from typing import Iterable

import numpy
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track

import polytune.environment as ENV
from polytune.convergence.plugin import ConvergencePlugin
from polytune.measurement.measurer import Measurer
from polytune.models.result import Result
from polytune.search.renderer import Renderer
from polytune.search.searcher import Searcher
from polytune.storages import Storage

log = logging.getLogger(__name__)


def f(cfg, measurer):
    return measurer.run_test(cfg)


class Runner:
    def __init__(self, searcher: Searcher, measurer: Measurer, storage: Storage):
        self.searcher = searcher
        self.measurer = measurer
        self.storage = storage

        self.tests_count = 0

        self.impacts_history = numpy.array([])
        self.warmup_tests_count = ENV.test_limit // 5
        self.impact_threshold = 0.005
        self.without_new_best = 0
        self.without_new_best_threshold = ENV.test_limit // 5
        self.convergence_plugins = []

        self.console = Console()

    def add_convergence_plugin(self, plugin: ConvergencePlugin):
        self.convergence_plugins.append(plugin)

    @property
    def workload(self):
        return self.searcher.workload

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
                results = p.starmap(f, zip(suggested_cfgs, repeat(self.measurer)))

            results = map(Result.get, results)

            generated = list()

            for config, result in zip(suggested_cfgs, results):
                self.searcher.tell(config, result)
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

        progress_wrapper = track(
            self._process_wrapper(),
            description="tests count",
            total=ENV.test_limit,
            transient=True,
            update_period=0.01,
        )

        for suggested, cfg, run_result in progress_wrapper:
            is_new_best = self.storage.insert_result(cfg, run_result)
            best_config = self.storage.best_configuration()
            best_result = self.storage.get_result(best_config)

            if is_new_best:
                for plugin in self.convergence_plugins:
                    plugin.on_new_best_result(cfg, run_result)

                dumped = best_config.render(self.searcher.space, Renderer)
                log.info(f"[green]New best:\n{dumped}\nwith result: \n{best_result}")

                self.without_new_best = 0
            else:
                self.without_new_best += 1

        log.info("Tuning was finished.")

        workload_name = ENV.workload_name.replace("/", "_").replace(":", "").replace('__', '_')
        dt_string = datetime.now().strftime("%d-%m-%Y_%H:%M")
        output_filename = f"{workload_name}_{dt_string}.csv"
        dataframes_folder = os.path.join(os.getcwd(), "tuning_dataframes")
        os.makedirs(dataframes_folder, exist_ok=True)

        with open(os.path.join(dataframes_folder, output_filename), "w") as output_file:
            dict_writer = csv.DictWriter(
                output_file,
                fieldnames=["id", "time", "timestamp", *self.searcher.space.name2param.keys()],
                restval="-",
                delimiter=",",
            )
            dict_writer.writeheader()
            dict_writer.writerows(self.storage.results_list())

        log.info(f"Tuning dataframe was written in {output_filename}.")

        best_config = self.storage.best_configuration()

        if best_config:
            md = Markdown(f"# Best configuration")
            self.console.print(md)
            self.console.print(
                f"[green][bold]{best_config.render(self.searcher.space, Renderer)}"
            )
