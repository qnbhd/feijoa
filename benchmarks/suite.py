import logging
import os
import platform
import random
import socket
import sys
import time
from typing import List, Dict

from benchmarks.trials import BenchesStorage
import click
import memory_profiler
import numpy as np
import numpy.random
import pandas as pd
from paretoset import paretorank
from paretoset import paretoset
from problem import Problem
import psutil

from feijoa import create_job
from feijoa.utils.logging import init

from problems import (
    Beale, Rastrigin, Rosenbrock, Sphere,
    Uni1, Uni2, Acley, Holder, IrisKNN

)

init(verbose=True)


log = logging.getLogger(__name__)

pd.set_option("display.max_colwidth", None)


class Suite:
    def __init__(self, db_url):
        self.optimizers: List[str] = list()
        self.problems: Dict[Problem] = dict()
        self.storage = BenchesStorage(db_url)
        self.machine_id = self.storage.insert_machine(
            **get_machine_info()
        )
        self.iterations = 30
        self.iterations_pool = dict()

    def add_problem(self, problem, *, name=None, iterations=100):
        name = name or problem.name
        self.problems[name] = problem
        self.iterations_pool[name] = iterations

    def add_optimizer(self, optimizer):
        self.optimizers.append(optimizer)

    def run(self):
        numpy.random.seed(0)
        random.seed(0)

        results = {
            "optimizer": [],
            "problem": [],
            "best": [],
            "mem_peak": [],
            "mem_mean": [],
            "iterations": [],
            "time": [],
            "dist": [],
            "iterations_before_best": [],
        }

        #
        # log.info('-' * 30)
        # log.info('Starting warmup stage')
        # log.info('-' * 30)
        #
        # job = create_job(
        #     search_space=self.problems[0].space,
        #     storage=f'sqlite:///:memory:',
        # )
        #
        # job.do(self.problems[0].evaluate, n_trials=20, n_jobs=-1, optimizer='bayesian')
        #
        # log.info('-' * 30)
        # log.info('Starting main stage')
        # log.info('-' * 30)

        for problem_name, problem in self.problems.items():
            trial_indexes = []

            for optimizer in self.optimizers:
                is_exists = self.storage.is_exists_trial(
                    problem_name,
                    optimizer,
                    self.machine_id,
                    self.iterations_pool[problem_name],
                )

                if is_exists:
                    log.warning(
                        f"Trial with problem: `{problem_name}`,"
                        f" optimizer: `{optimizer}`,"
                        f" machine id: `{self.machine_id}`,"
                        f" iterations: `{self.iterations}`"
                        " was skipped because result exists."
                    )
                    continue

                job = create_job(
                    search_space=problem.space,
                    name=optimizer,
                    storage=f"sqlite:///:memory:",
                )

                start = time.monotonic()

                # noinspection PyBroadException
                try:
                    mem_usage = memory_profiler.memory_usage(
                        (
                            job.do,
                            (problem.evaluate,),
                            {
                                "n_trials": self.iterations_pool[
                                    problem_name
                                ],
                                "n_jobs": -1,
                                "n_points_iter": 20,
                                "optimizer": optimizer,
                                "progress_bar": True,
                            },
                        ),
                        max_iterations=1,
                    )
                except Exception:
                    continue

                results["optimizer"].append(optimizer)
                results["problem"].append(problem_name)

                job_df = job.dataframe
                minima = job_df["objective_result"].argmin()
                iterations_before_best = int(job_df.iloc[minima].id)

                best = job.best_value
                mem_peak = np.max(mem_usage)
                mem_mean = np.mean(mem_usage)
                iterations = job.experiments_count
                time_ = time.monotonic() - start
                dist = np.abs(problem.solution[1] - job.best_value)

                results["best"].append(best)
                results["mem_peak"].append(mem_peak)
                results["mem_mean"].append(mem_mean)
                results["iterations"].append(iterations)
                results["time"].append(time_)
                results["dist"].append(dist)
                results["iterations_before_best"].append(
                    iterations_before_best
                )

                trial_id = self.storage.insert_trial(
                    self.machine_id,
                    problem_name,
                    optimizer,
                    best,
                    mem_peak,
                    mem_mean,
                    iterations,
                    time_,
                    dist,
                    iterations_before_best,
                )

                trial_indexes.append(trial_id)

            pareto_ranking = []

            total_df = pd.DataFrame.from_dict(results)
            problem_df = total_df[
                total_df["problem"] == problem_name
            ][["best", "time", "mem_mean", "dist"]]
            ranks = paretorank(
                problem_df, sense=["min", "min", "min", "min"]
            )
            pareto_ranking.extend(ranks)

            for trial_id, rank in zip(trial_indexes, pareto_ranking):
                self.storage.set_pareto_ranking(trial_id, rank)

        total_df = pd.DataFrame.from_dict(results)

        # pareto_ranking = []
        #
        # for problem in set(results['problem']):
        #     problem_df = total_df[total_df['problem'] == problem][['best', 'time', 'mem_mean', 'dist']]
        #     ranks = paretorank(problem_df, sense=["min", "min", "min", "min"])
        #     pareto_ranking.extend(ranks)
        #
        # assert len(pareto_ranking) == len(results['optimizer'])
        #
        # total_df['pareto_ranking'] = pareto_ranking
        #
        # for trial_id, rank in zip(trial_indexes, pareto_ranking):
        #     self.storage.set_pareto_ranking(trial_id, rank)

        return total_df

    def load_dataframe(self):
        results = self.storage.load_trials()
        return pd.DataFrame.from_dict(results)

    def get_total_ranking(self):
        return pd.DataFrame.from_dict(
            self.storage.get_total_ranking()
        )


@click.group()
def cli():
    pass


@click.command()
@click.option("--database", type=str, required=True)
def run(database):
    test_suite = Suite(database)

    for i in [10, 15, 20, 50, 100, 300]:
        test_suite.add_problem(Rosenbrock(), iterations=i, name=f'rosen_{i}')
        test_suite.add_problem(Rastrigin(), iterations=i, name=f'rastrigin_{i}')
        test_suite.add_problem(Beale(), iterations=i, name=f'beale_{i}')
        test_suite.add_problem(Sphere(), iterations=i, name=f'sphere_{i}')
        test_suite.add_problem(Uni1(), iterations=i, name=f'uni1_{i}')
        test_suite.add_problem(Uni2(), iterations=i, name=f'uni2_{i}')
        test_suite.add_problem(Acley(), iterations=i, name=f'ackley_{i}')
        test_suite.add_problem(Holder(), iterations=i, name=f'holder_{i}')
        test_suite.add_problem(IrisKNN(), iterations=i, name=f'irisknn_{i}')

    test_suite.add_optimizer("bayesian[acq=lfboei]")
    test_suite.add_optimizer("bayesian[acq=lfbopoi]")
    test_suite.add_optimizer("bayesian[acq=ucb]")
    test_suite.add_optimizer("bayesian[acq=poi]")
    test_suite.add_optimizer("bayesian")
    test_suite.add_optimizer("bayesian[acq=lfboei]+reducer")
    test_suite.add_optimizer("bayesian[acq=lfbopoi]+reducer")
    test_suite.add_optimizer("bayesian[acq=ucb]+reducer")
    test_suite.add_optimizer("bayesian[acq=poi]+reducer")
    test_suite.add_optimizer("bayesian+reducer")
    test_suite.add_optimizer("cmaes")
    test_suite.add_optimizer("grid")
    test_suite.add_optimizer("pattern")
    test_suite.add_optimizer("pso")
    test_suite.add_optimizer("ucb<bayesian,cmaes,pso,random>")
    test_suite.add_optimizer("de")
    test_suite.add_optimizer("brkga")
    test_suite.add_optimizer("nichega")
    test_suite.add_optimizer("sres")
    test_suite.add_optimizer("isres")
    test_suite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]>"
    )
    test_suite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]+reducer>"
    )

    df = test_suite.run()
    print(df)

    print(
        test_suite.get_total_ranking().sort_values(
            by="ranking", ascending=False
        )
    )


@click.command()
@click.option("--database", type=str, required=True)
def load_dataframe(database):
    suite = Suite(database)
    df = suite.load_dataframe()
    print(df)


cli.add_command(run)
cli.add_command(load_dataframe)


def get_machine_info():
    return {
        "name": socket.gethostname(),
        "sys_platform": sys.platform,
        "architecture": platform.machine(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "os_release": platform.release(),
        "total_cpus": psutil.cpu_count(),
        "physical_cpus": psutil.cpu_count(logical=False),
        "ram": psutil.virtual_memory().total,
        "cpu_freq_min": psutil.cpu_freq().min,
        "cpu_freq_max": psutil.cpu_freq().max,
    }


if __name__ == "__main__":
    cli()
