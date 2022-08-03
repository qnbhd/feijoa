from feijoa import create_job
from feijoa import Experiment
from feijoa import Real
from feijoa import SearchSpace


# noinspection DuplicatedCode
def test_seed():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Real("y", low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get("x", 5.0)
        y = params.get("y", 5.0)

        return (1 - x) ** 2 + (1 - y) ** 2

    job = create_job(search_space=space)
    job.add_seed({"x": 1.0, "y": 1.0})
    job.do(objective, n_trials=50, n_proc=1, algo_list=["grid"])

    assert job.best_parameters == {"x": 1.0, "y": 1.0}
    # assert job.best_experiment.requestor == "SeedAlgorithm"
