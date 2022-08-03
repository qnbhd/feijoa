from feijoa import Categorical
from feijoa import create_job
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace


def test_grid_search():
    space = SearchSpace()
    space.insert(Integer("x", low=0, high=2))
    space.insert(Real("y", low=0.0, high=0.5))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    def objective(experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        z = experiment.params.get("z")

        return -(x + y + (2 if z == "foo" else 1))

    # let's assume EPS = 0.1
    # all combinations count: 3 * ((0.5 - 0) / 0.1 + 1) * 2 = 3 * 6 * 2 = 36
    # needed n_trials = 36 but for coverage we take greater than 36
    # total experiments must be 36

    job = create_job(search_space=space)
    job.do(objective, n_trials=50, algo_list=["grid"])

    experiments_params = [e.params for e in job.experiments]

    # exhaustive search
    assert experiments_params == [
        {"x": 0, "y": 0.0, "z": "foo"},
        {"x": 0, "y": 0.0, "z": "bar"},
        {"x": 0, "y": 0.1, "z": "foo"},
        {"x": 0, "y": 0.1, "z": "bar"},
        {"x": 0, "y": 0.2, "z": "foo"},
        {"x": 0, "y": 0.2, "z": "bar"},
        {"x": 0, "y": 0.3, "z": "foo"},
        {"x": 0, "y": 0.3, "z": "bar"},
        {"x": 0, "y": 0.4, "z": "foo"},
        {"x": 0, "y": 0.4, "z": "bar"},
        {"x": 0, "y": 0.5, "z": "foo"},
        {"x": 0, "y": 0.5, "z": "bar"},
        {"x": 1, "y": 0.0, "z": "foo"},
        {"x": 1, "y": 0.0, "z": "bar"},
        {"x": 1, "y": 0.1, "z": "foo"},
        {"x": 1, "y": 0.1, "z": "bar"},
        {"x": 1, "y": 0.2, "z": "foo"},
        {"x": 1, "y": 0.2, "z": "bar"},
        {"x": 1, "y": 0.3, "z": "foo"},
        {"x": 1, "y": 0.3, "z": "bar"},
        {"x": 1, "y": 0.4, "z": "foo"},
        {"x": 1, "y": 0.4, "z": "bar"},
        {"x": 1, "y": 0.5, "z": "foo"},
        {"x": 1, "y": 0.5, "z": "bar"},
        {"x": 2, "y": 0.0, "z": "foo"},
        {"x": 2, "y": 0.0, "z": "bar"},
        {"x": 2, "y": 0.1, "z": "foo"},
        {"x": 2, "y": 0.1, "z": "bar"},
        {"x": 2, "y": 0.2, "z": "foo"},
        {"x": 2, "y": 0.2, "z": "bar"},
        {"x": 2, "y": 0.3, "z": "foo"},
        {"x": 2, "y": 0.3, "z": "bar"},
        {"x": 2, "y": 0.4, "z": "foo"},
        {"x": 2, "y": 0.4, "z": "bar"},
        {"x": 2, "y": 0.5, "z": "foo"},
        {"x": 2, "y": 0.5, "z": "bar"},
    ]
