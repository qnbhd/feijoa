import click

import qutune.environment
from qutune.measurement.measurer import Measurer
from qutune.runner import Runner
from qutune.search.searcher import Searcher
import qutune.search.space
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

    environment = qutune.environment.Environment()
    environment.load_from_file(prop)
    environment.set('processes_count', processes)

    wargs = qutune.environment.workload_args or dict()

    workload = workloadFactory(
        qutune.environment.workload_name,
        **wargs)

    space_yaml = qutune.environment.space

    space = qutune.search.space.from_yaml(space_yaml)

    searcher = Searcher(workload, space)
    measurer = Measurer(workload)

    runner = Runner(searcher, measurer)

    runner.process()


cli.add_command(run)

if __name__ == '__main__':
    cli()
