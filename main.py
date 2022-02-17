import os

import click

from examples.rosenbrock.runner import METRICS, rosenbrock_objective as objective
from polytune import __project_folder__
from polytune.jobs import create_job, load_job
from polytune.models.experiment import Experiment
from polytune.search.space import from_yaml


@click.group()
def cli():
    pass


# @click.command()
# @click.option("--verbose", "-v", is_flag=True)
# @click.option("-p", 'processes', type=int, default=1)
# def run(verbose, processes):
#     logging.init(verbose)
#
#     dt_string = datetime.now().strftime("%d-%m-%Y_%H:%M")
#
#     tuning_dbs_folder = os.path.join(abspath(dirname(__file__)), "tuning_dbs")
#     os.makedirs(tuning_dbs_folder, exist_ok=True)
#     storage_path = os.path.join(tuning_dbs_folder, f'tuning_{dt_string}_{uuid.uuid4().hex}.json')
#     storage = TinyDBStorage(storage_path)
#
#     searcher = Searcher(SPACE, storage)
#
#     def objective(x: Experiment) -> float:
#         return x['time']
#
#     runner = Runner(
#         searcher,
#         storage,
#         metric_collector,
#         METRICS,
#         objective
#     )
#
#     runner.process()
#

@click.command()
def run():
    yml_file = os.path.join(__project_folder__, 'examples', 'rosenbrock', 'space.yaml')
    space = from_yaml(yml_file)
    job = create_job(space)

    # job = load_job(space, 'foo', 'foo')
    # print(job.experiments_count)
    # print(job.best_experiment)
    # exit(0)
    job.do(objective, n_trials=10)
    print(job.best_parameters)


cli.add_command(run)
# cli.add_command(run_v2)

if __name__ == '__main__':
    cli()
