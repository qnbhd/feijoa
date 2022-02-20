import click
from polytune import create_job, Experiment, SearchSpace, Real


@click.group()
def cli():
    pass


@click.command()
def run():
    space = SearchSpace()
    space.add_parameter(Real('x', low=0.0, high=1.0))
    space.add_parameter(Real('y', low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get('x', 5.0)
        y = params.get('y', 5.0)

        return (1 - x) ** 2 + (1 - y) ** 2

    job = create_job(space)
    job.add_seed({'x': 1.0, 'y': 1.0})
    job.do(objective, n_trials=50, n_proc=1, algo_list=['grid'])

    print(job.dataframe)


cli.add_command(run)

if __name__ == '__main__':
    cli()
