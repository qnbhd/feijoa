import click

import polytune.environment
import polytune.search.space
from polytune.measurement.measurer import Measurer
from polytune.models.configuration import Configuration
from polytune.runner import Runner
from polytune.search.searcher import Searcher
from polytune.storages.memory import MemoryStorage
from utils import logging
from workloads import workload_factory


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

    wargs = polytune.environment.workload_args or dict()

    workload = workload_factory(
        polytune.environment.workload_name,
        **wargs)

    space_yaml = polytune.environment.space

    space = polytune.search.space.from_yaml(space_yaml)

    storage = MemoryStorage()

    searcher = Searcher(workload, space, storage)
    measurer = Measurer(workload, space)

    runner = Runner(searcher, measurer, storage)
    # runner.add_convergence_plugin(ImpactsHistoryPlugin())

    runner.process()


cli.add_command(run)

if __name__ == '__main__':
    cli()
