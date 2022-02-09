import click

import polytune.environment
from polytune.measurement.measurer import Measurer
from polytune.runner import Runner
from polytune.search.searcher import Searcher
import polytune.search.space
from utils import logging
from workloads import workloadFactory


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

    workload = workloadFactory(
        polytune.environment.workload_name,
        **wargs)

    space_yaml = polytune.environment.space

    space = polytune.search.space.from_yaml(space_yaml)

    searcher = Searcher(workload, space)
    measurer = Measurer(workload)

    runner = Runner(searcher, measurer)

    runner.process()


cli.add_command(run)

if __name__ == '__main__':
    cli()
