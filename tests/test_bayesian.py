from feijoa import Categorical
from feijoa import create_job
from feijoa import Integer
from feijoa import Real
from feijoa import SearchSpace
from feijoa.search.algorithms.bayesian import BayesianAlgorithm


def test_bayesian_search():
    space = SearchSpace()

    space.insert(Integer("x", low=0, high=2))
    space.insert(Real("y", low=0.0, high=0.5))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    def objective(experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        z = experiment.params.get("z")

        return -(x + y + (2 if z == "foo" else 3))

    job = create_job(search_space=space)
    job.do(objective, n_trials=50, algo_list=["bayesian"])


# noinspection DuplicatedCode
def test_specify_acq_bayesian_search():
    space = SearchSpace()

    space.insert(Integer("x", low=0, high=2))
    space.insert(Real("y", low=0.0, high=0.5))
    space.insert(Categorical("z", choices=["foo", "bar"]))

    def objective(experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        z = experiment.params.get("z")

        return -(x + y + (2 if z == "foo" else 3))

    job = create_job(search_space=space)

    a_ei = BayesianAlgorithm(
        search_space=job.search_space, acq_function="ei"
    )

    job.do(objective, n_trials=10, algo_list=[a_ei])

    a_poi = BayesianAlgorithm(
        search_space=job.search_space, acq_function="poi"
    )

    job.do(objective, n_trials=10, algo_list=[a_poi])

    a_ucb = BayesianAlgorithm(
        search_space=job.search_space, acq_function="ucb"
    )

    job.do(objective, n_trials=10, algo_list=[a_ucb])
