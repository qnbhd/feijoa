from collections import defaultdict
from collections import namedtuple
from itertools import product
import logging
import random
import time

from benchmarks.storage import BenchmarksStorage
from benchmarks.suite import get_machine_info
from benchmarks.trials import BenchesStorage
from benchmarks.utils import pickup_problems
import click as click
import memory_profiler
import numpy as np
import pandas as pd
from paretoset import paretorank
from rich.console import Console
from scipy.special import softmax

from feijoa import create_job
from feijoa.utils.logging import init


init(verbose=True)

log = logging.getLogger(__name__)

console = Console()


def norm(y, a=0.0, b=1.0):
    return (b - a) * (y - y.min()) / (y.max() - y.min()) + a


def ffiz(x):
    return (
        14.01781
        - 0.184
        + (1.184433 - 14.01781)
        / (1 + ((x - 0.09) / 0.708392) ** 4.232001) ** 0.884245
    )


def ffee(x):
    return 1 / (1 + np.abs(x - 1) ** 10)


class BenchmarkSuite:
    def __init__(self, db_url):
        self.optimizers = list()
        self.storage = BenchmarksStorage(db_url)
        self.machine_id = self.storage.put_machine(
            **get_machine_info()
        )

    def add_optimizer(self, optimizer):
        self.optimizers.append(optimizer)

    def do(self, randomized=False, k=10):
        trials = defaultdict(list)

        Problem = namedtuple(
            "Problem",
            [
                "fun",
                "name",
                "space",
                "group",
                "iterations",
                "solution",
            ],
        )

        picked = [
            [
                Problem(
                    fun, name, space, group, iterations, solution
                ),
                optimizer,
            ]
            for optimizer in (
                random.choices(self.optimizers, k=k)
                if randomized
                else self.optimizers
            )
            for (fun, name, space, group, iterations, solution) in (
                random.choices(pickup_problems(), k=k)
                if randomized
                else pickup_problems()
            )
        ]

        for problem, optimizer in picked:
            iterations = problem.iterations
            problem_id = self.storage.put_problem(
                problem.name,
                problem.space.card,
                len(problem.space),
                problem.group,
                iterations,
            )
            optimizer_id = self.storage.put_optimizer(optimizer)

            is_exists = self.storage.is_exists_trial(
                problem_id, optimizer_id, self.machine_id
            )

            if is_exists:
                continue

            log.info(
                f"Start new task: {problem.name} with"
                f" optimizer: {optimizer}, iterations: {iterations}"
            )

            job = create_job(
                search_space=problem.space,
                name=f"{problem.name}_{optimizer}",
                storage="sqlite:///:memory:",
            )

            start = time.monotonic()

            def evaluator(experiment):
                return problem.fun(**experiment.params)

            # noinspection PyBroadException
            try:
                np.random.seed(0)
                random.seed(0)
                mem_usage = memory_profiler.memory_usage(
                    (
                        job.do,
                        (evaluator,),
                        {
                            "n_trials": iterations,
                            "n_jobs": -1,
                            "n_points_iter": 20,
                            "optimizer": optimizer,
                            "progress_bar": True,
                        },
                    ),
                    max_iterations=1,
                )
            except Exception as e:
                log.critical("Error occured")
                print(e)
                console.print_exception(max_frames=20)
                continue

            best = job.best_value
            mem_peak = np.max(mem_usage)
            mem_mean = np.mean(mem_usage)
            time_ = time.monotonic() - start
            dist = np.abs(problem.solution - job.best_value)

            try:
                trial_uuid = self.storage.put_trial(
                    self.machine_id,
                    optimizer_id,
                    problem_id,
                    best,
                    mem_peak,
                    mem_mean,
                    time_,
                    dist,
                    job.rewards,
                )
                self.storage.put_results(trial_uuid, job.experiments)
            except Exception as e:
                log.critical("let's wait a little bit ....")
                raise e

            # current_df = pd.DataFrame.from_dict(current_trials)
            # pareto_ranking = self.calculate_pareto_ranking(current_df, problem.name)

            # for trial_id, rank in zip(trial_indices, pareto_ranking):
            #     self.storage.set_pareto_ranking(trial_id, rank)
            #
            # for col, val in current_trials.items():
            #     trials[col].append(val)

        return pd.DataFrame.from_dict(trials)

    @staticmethod
    def calculate_pareto_ranking(df, problem_name, features):
        directions, metrics = [], []

        for feature in features:
            metric, direction = feature.split(":")
            directions.append(direction)
            metrics.append(metric)

        ranks = norm(
            sum(
                norm(df[tm]) * (-1 if direction == "min" else 1)
                for tm, direction in zip(metrics, directions)
            )
        )

        df["rank"] = ranks

        if problem_name == "all":
            problems_count = len(df["problem"].unique())

            for opt in df["optimizer"].unique():
                opt_df = df[df["optimizer"] == opt]
                pr = len(opt_df["problem"].unique())
                if pr < problems_count / 3:
                    log.info(f"Remove {opt}")
                    df.drop(opt_df.index, inplace=True)

            ret_df = (
                BenchmarkSuite.calculate_avg_ranking_for_optimizers(
                    df
                )
            )

            # ret_df.loc[df['rank'] == df['rank'].max(), 'rank'] *= 1.05
            ret_df["rank"] = norm(softmax(ret_df["rank"]))

            return ret_df

        data = defaultdict(list)

        for optimizer in df["optimizer"].unique():
            grouped = df[df["optimizer"] == optimizer]
            mean_rank = grouped["rank"].mean()
            for col in grouped.columns:
                if col != "rank":
                    data[col].append(grouped[col].iloc[0])
            data["rank"].append(mean_rank)

        ret_df = pd.DataFrame.from_dict(data)

        # ret_df.loc[df['rank'] == df['rank'].max(), 'rank'] *= 1.05
        ret_df["rank"] = norm(softmax(ret_df["rank"]))

        return ret_df

    def load_dataframe(self):
        results = self.storage.fetch_trials()
        return pd.DataFrame.from_dict(results)

    @staticmethod
    def calculate_avg_ranking_for_optimizers(dataframe):
        trials = defaultdict(list)

        for optimizer, problem in product(
            dataframe["optimizer"].unique(),
            dataframe["problem"].unique(),
        ):
            query = dataframe.query(
                f"optimizer == '{optimizer}' and"
                f" problem == '{problem}'"
            )

            mean_rank = query["rank"].mean()

            if not np.isfinite(mean_rank):
                continue

            trials["optimizer"].append(optimizer)
            trials["problem"].append(problem)
            trials["rank"].append(mean_rank)

        sdf = pd.DataFrame.from_dict(trials)

        results = defaultdict(list)

        for optimizer in dataframe["optimizer"].unique():
            res = sdf.query(f"optimizer == '{optimizer}'")["rank"]
            results["optimizer"].append(optimizer)
            results["rank"].append(res.mean())

        tdf = pd.DataFrame.from_dict(results)

        return tdf


@click.group()
def cli():
    pass


@click.command()
@click.option("--database", type=str, required=True)
def run(database):
    test_suite = BenchmarkSuite(database)

    test_suite.add_optimizer("bayesian[acq=lfboei]")
    test_suite.add_optimizer("bayesian[acq=lfbopoi]")
    test_suite.add_optimizer("bayesian[acq=ucb]")
    test_suite.add_optimizer("cmaes")
    test_suite.add_optimizer("skopt")
    test_suite.add_optimizer("pattern")
    test_suite.add_optimizer("pso")
    test_suite.add_optimizer("ucb<bayesian,cmaes>")
    test_suite.add_optimizer("ucb<bayesian+reducer,cmaes>")
    test_suite.add_optimizer("ucb<bayesian[acq=lfbopoi],cmaes>")
    test_suite.add_optimizer("ucb<bayesian,pso>")
    test_suite.add_optimizer("ucb<bayesian[acq=lfbopoi],pso>")
    test_suite.add_optimizer("th<pso,cmaes>")
    test_suite.add_optimizer("de")
    test_suite.add_optimizer("nichega")
    test_suite.add_optimizer("isres")
    test_suite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]>"
    )
    test_suite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]+reducer>"
    )
    test_suite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor], pso>"
    )

    df = test_suite.do(randomized=True)
    print(df)

    print(
        test_suite.get_total_ranking().sort_values(
            by="ranking", ascending=False
        )
    )


@click.command()
@click.option("--database", type=str, required=True)
def load_dataframe(database):
    suite = BenchmarkSuite(database)
    df = suite.load_dataframe()
    print(df)


@click.command()
@click.option("--database", type=str, required=True)
@click.option("--problem", type=str, required=True)
@click.option("--iterations", type=int, default=None)
@click.option("--feature", "features", type=str, multiple=True)
def calculate_ranking(database, problem, iterations, features):
    print(features)

    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.max_rows", 500)
    pd.set_option("display.max_columns", 500)
    pd.set_option("display.width", 1000)
    pd.set_option("display.float_format", lambda x: "%.5f" % x)

    features = ["best:min"]

    directions = []
    metrics = []

    for feature in features:
        metric, direction = feature.split(":")
        directions.append(direction)
        metrics.append(metric)

    storage = BenchesStorage(database)
    trials = storage.load_trials(problem, iterations)
    dataframe = pd.DataFrame.from_dict(trials)
    dataframe.drop(columns=["pareto_ranking"], inplace=True)
    problem_df = dataframe[metrics]
    ranks = paretorank(problem_df, sense=directions)
    print(dataframe.columns)
    dataframe["rank"] = [1 / rank for rank in ranks]
    print(dataframe[["problem", "best", "optimizer", "rank"]])


cli.add_command(run)
cli.add_command(load_dataframe)
cli.add_command(calculate_ranking)

if __name__ == "__main__":

    bsuite = BenchmarkSuite("sqlite:///test.db")

    bsuite.add_optimizer("bcmaes")
    bsuite.add_optimizer("optuna_nsgaii")
    bsuite.add_optimizer("optuna_cmaes")
    bsuite.add_optimizer("optuna_motpe")
    bsuite.add_optimizer("opentuner")
    bsuite.add_optimizer("hyperopt")
    bsuite.add_optimizer("pysot")
    bsuite.add_optimizer("opentuner")

    bsuite.add_optimizer("pattern")
    bsuite.add_optimizer("pso")
    bsuite.add_optimizer("ucb<bayesian,cmaes>")
    bsuite.add_optimizer("ucb<bayesian+reducer,cmaes>")
    bsuite.add_optimizer("ucb<bayesian[acq=lfbopoi],cmaes>")
    bsuite.add_optimizer("ucb<bayesian,pso>")
    bsuite.add_optimizer("ucb<bayesian[acq=lfbopoi],pso>")
    bsuite.add_optimizer("th<pso,cmaes>")
    bsuite.add_optimizer("de")
    bsuite.add_optimizer("nichega")
    bsuite.add_optimizer("isres")
    bsuite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]>"
    )
    bsuite.add_optimizer(
        "ucb<bayesian[acq=lfboei, regr=RandomForestRegressor]+reducer>"
    )

    bsuite.do(randomized=True, k=100)
