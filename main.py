import click

from qutune.environment import Environment
from qutune.measurement.measurer import Measurer
from qutune.runner import Runner
from qutune.search.searcher import Searcher
import qutune.search.space
from utils import logging
from workloads import get_workload

@click.group()
def cli():
    pass

@click.command()
@click.option("--env", type=str, required=True)
def run(env):
    logging.init()

    environment = Environment()
    environment.load_from_file(env)

    workload = get_workload(environment.workload_name)
    space_yaml = environment.space

    space = qutune.search.space.from_yaml(space_yaml)

    searcher = Searcher(workload, space)
    measurer = Measurer(workload)

    runner = Runner(searcher, measurer)

    runner.process()

cli.add_command(run)

if __name__ == '__main__':
    cli()
