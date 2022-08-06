from feijoa import create_job
from feijoa import Experiment
from feijoa import Real
from feijoa import SearchSpace
from feijoa.models.configuration import Configuration
from feijoa.models.experiment import ExperimentState
from feijoa.storages.rdb.storage import RDBStorage


def test_rdb_storage():
    storage = RDBStorage("sqlite:///:memory:")

    class _Job:
        def __init__(self, job_id, job_name):
            self.id = job_id
            self.name = job_name
            self.search_space = SearchSpace()
            self.search_space.insert(Real("x", low=0.0, high=1.0))
            self.search_space.insert(Real("y", low=0.0, high=1.0))

    ex = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params=Configuration({"x": 0.0, "y": 1.0}),
    )

    ex_2 = Experiment(
        id=0,
        job_id=1,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params=Configuration({"x": 0.0, "y": 1.0}),
    )

    mock_job = _Job(0, "foo")
    mock_job_2 = _Job(1, "boo")

    storage.insert_job(mock_job)
    storage.insert_job(mock_job_2)

    storage.insert_experiment(ex)
    storage.insert_experiment(ex_2)

    assert storage.get_experiments_by_job_id(0) == [ex]
    assert storage.get_experiments_by_job_id(1) == [ex_2]

    assert storage.get_experiment(job_id=0, experiment_id=0) == ex

    assert storage.jobs == [
        {"id": 0, "name": "foo"},
        {"id": 1, "name": "boo"},
    ]


def test_integrated_rdb_storage():
    space = SearchSpace()
    storage = RDBStorage("sqlite:///:memory:")

    # noinspection DuplicatedCode
    def objective(experiment: Experiment):
        x = experiment.params.get("x")
        y = experiment.params.get("y")
        return (
            (1.5 - x + x * y) ** 2
            + (2.25 - x + x * y**2) ** 2
            + (2.625 - x + x * y**3) ** 2
        )

    space.insert(Real("x", low=0.0, high=5.0))
    space.insert(Real("y", low=0.0, high=2.0))

    job = create_job(search_space=space, storage=storage)
    job.do(objective, n_trials=5)

    print(job.dataframe)
