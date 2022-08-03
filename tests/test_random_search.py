from feijoa import Categorical
from feijoa import create_job
from feijoa import Experiment
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace


def faked_random(nums):
    f = fake_random(nums)

    def inner(*args, **kwargs):
        return next(f)

    return inner


def fake_random(nums):
    i = 0
    while True:
        yield nums[i]
        i = (i + 1) % len(nums)


def test_random_search():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Real("y", low=0.0, high=1.0))
    space.insert(Integer("z", low=0, high=2))
    space.insert(Categorical("w", choices=["foo"]))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get("x")
        y = params.get("y")

        return (1 - x) ** 2 + (1 - y) ** 2

    job = create_job(search_space=space)
    job.do(objective, n_trials=10, algo_list=["random"])

    assert job.best_parameters == {
        "w": "foo",
        "x": 0.8444218515250481,
        "y": 0.7579544029403025,
        "z": 1,
    }
