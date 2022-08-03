from feijoa import Categorical
from feijoa import create_job
from feijoa import Experiment
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace


def objective(experiment: Experiment):
    x = experiment.params.get("x")
    y = experiment.params.get("y")
    z = experiment.params.get("z")

    a = 0
    if z == "foo":
        a = 1
    if z == "bar":
        a = -1

    return (
        (1.5 - x + x * y) ** 2
        + (2.25 - x + x * y**2) ** 2
        + (2.625 - x + x * y**3) ** 2
        + a
    )


def test_template_search():
    space = SearchSpace()

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Integer("y", low=0, high=2))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    job = create_job(search_space=space)
    job.do(objective, n_trials=200, algo_list=["template"])
