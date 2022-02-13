import os
import uuid
from datetime import datetime
from os.path import abspath, dirname

import click

import polytune.environment
import polytune.search.space
from polytune.models.result import Result
from polytune.runner import Runner
from polytune.search.searcher import Searcher
from polytune.storages.tiny import TinyDBStorage
from utils import logging
from workloads.gcc.runner import metric_collector, METRICS, SPACE


@click.group()
def cli():
    pass


@click.command()
@click.argument("prop", required=True)
@click.option("--verbose", "-v", is_flag=True)
@click.option("-p", 'processes', type=int, default=1)
def run(prop, verbose, processes):
    logging.init(verbose)

    environment = polytune.environment.Environment()
    environment.load_from_file(prop)
    environment.set('processes_count', processes)

    polytune.environment.workload_args = polytune.environment.workload_args or dict()

    dt_string = datetime.now().strftime("%d-%m-%Y_%H:%M")

    tuning_dbs_folder = os.path.join(abspath(dirname(__file__)), "tuning_dbs")
    os.makedirs(tuning_dbs_folder, exist_ok=True)
    storage_path = os.path.join(tuning_dbs_folder, f'tuning_{dt_string}_{uuid.uuid4().hex}.json')
    storage = TinyDBStorage(storage_path)

    searcher = Searcher(SPACE, storage)

    def objective(x: Result) -> float:
        return x['time']

    runner = Runner(
        searcher,
        storage,
        metric_collector,
        METRICS,
        objective
    )

    runner.process()


cli.add_command(run)

if __name__ == '__main__':
    cli()
