from gimeltune import create_job, Experiment, SearchSpace, Real


def objective(experiment: Experiment):
    x = experiment.params.get('x')
    y = experiment.params.get('y')
    return (1.5 - x + x*y)**2 + (2.25 - x + x*y**2)**2 + (2.625 - x + x*y**3)**2


def test_minimal():
    space = SearchSpace()

    space.insert(Real(f'x', low=0.0, high=5.0))
    space.insert(Real(f'y', low=0.0, high=2.0))

    job = create_job(search_space=space, storage='tinydb:///foo.json')
    job.do(objective, n_trials=50)

    assert abs(job.best_value - 0) < 2
