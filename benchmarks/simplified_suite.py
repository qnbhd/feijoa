import logging
import random
import time
from collections import defaultdict, namedtuple

import numpy as np

from benchmarks.suite import get_machine_info
from benchmarks.trials import BenchesStorage
from benchmarks.utils import pickup_problems, bench, group, iterations
from rich.progress import Progress

from feijoa.utils.logging import init

init(verbose=True)

log = logging.getLogger(__name__)


class BenchmarkSuite:

    def __init__(self, db_url):
        self.optimizers = list()
        # self.storage = BenchesStorage(db_url)
        # self.machine_id = self.storage.insert_machine(
        #     **get_machine_info()
        # )

    def add_optimizer(self, optimizer):
        self.optimizers.append(optimizer)

    def do(self, randomized=False, k=10):
        trials = defaultdict(list)

        Problem = namedtuple('Problem', ['fun', 'name', 'space', 'group', 'iterations'])

        picked = [

            [
                Problem(fun, name, space, group, iterations),
                optimizer
            ]
            for optimizer
            in (
               random.choices(self.optimizers, k=k)
               if randomized
               else self.optimizers
            )

            for
            (
                fun, name, space, group, iterations
            )
            in (
                random.choices(pickup_problems(), k=k)
                if randomized
                else pickup_problems()
            )
        ]

        np.random.seed(0)
        random.seed(0)

        # with Progress() as progress:
        #
        #     task1 = progress.add_task("[red]Downloading...", total=1000)
        #
        #     while not progress.finished:
        #         progress.update(task1, advance=0.5)
        #         time.sleep(0.02)

        for problem, optimizer in picked:
            log.info(f"Start new task: {problem.name} with optimizer: {optimizer}")

            with Progress(transient=True) as progress:
                task1 = progress.add_task("Downloading...", total=10)
                while not progress.finished:
                    progress.update(task1, advance=0.5)
                    time.sleep(0.001)
                    log.debug('WOO')
                    log.info('HOO')
                    log.critical('ZOO')


if __name__ == '__main__':
    suite = BenchmarkSuite('postgresql+psycopg2://postgres:'
                           'myPassword@188.124.39.245/postgres')

    suite.add_optimizer('bayesian')

    suite.do(randomized=True)






