from typing import List, Optional

import pytest

from gimeltune import (
    Experiment,
    Real,
    SearchAlgorithm,
    SearchSpace,
    TinyDBStorage,
    create_job,
    load_job,
)
from gimeltune.exceptions import (
    DuplicatedJobError,
    ExperimentNotFinishedError,
    InvalidStoragePassed,
    InvalidStorageRFC1738,
    JobNotFoundError,
    SearchAlgorithmNotFoundedError,
)
from gimeltune.jobs.job import _load_storage
from gimeltune.models.experiment import ExperimentState


def test_job():
    job = create_job(search_space=SearchSpace())

    job.setup_default_algo()

    assert job.best_experiment is None
    assert job.best_value is None
    assert job.best_parameters is None
    assert isinstance(job.experiments, list) and not job.experiments
    assert job.experiments_count == 0
    assert job.top_experiments(10) == []
    assert job.dataframe.empty


def test_create_load_job():
    space = SearchSpace()
    space.insert(Real("x", low=0.0, high=1.0))
    space.insert(Real("y", low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get("x")
        y = params.get("y")

        experiment.metrics = {
            "foo": 1.0,
            "bar": 2.0,
        }

        return (1 - x)**2 + (1 - y)**2

    job = create_job(search_space=space,
                     name="foo",
                     storage="sqlite:///foo.db")
    job.do(objective, n_trials=10, algo_list=["random"])

    assert isinstance(job.experiments, list) and len(job.experiments) == 10
    assert job.experiments_count == 10
    assert len(job.top_experiments(100)) == 10

    job2 = load_job(search_space=SearchSpace(),
                    name="foo",
                    storage="sqlite:///foo.db")

    assert isinstance(job2.experiments, list) and len(job2.experiments) == 10
    assert job2.experiments_count == 10
    assert len(job2.top_experiments(100)) == 10

    print(job2.dataframe)


def test_incorrect_algo_passed():
    space = SearchSpace()
    job = create_job(search_space=space)

    with pytest.raises(SearchAlgorithmNotFoundedError):
        job.do(lambda: 1, algo_list=["some_incorrect"])

    class IncorrectAlgo:
        def ask(self) -> Optional[List[Experiment]]:
            pass

        def tell(self, experiment: Experiment):
            pass

    with pytest.raises(SearchAlgorithmNotFoundedError):
        job.do(lambda: 1, algo_list=[IncorrectAlgo])


def test_correct_algo_subclass_passed():
    space = SearchSpace()
    job = create_job(search_space=space)

    class CorrectAlgo(SearchAlgorithm):
        def __init__(self, *args, **kwargs):
            pass

        def ask(self) -> Optional[List[Experiment]]:
            pass

        def tell(self, experiment: Experiment):
            pass

    job.do(lambda: 1, algo_list=[CorrectAlgo])


def test_no_configurations_warning():
    space = SearchSpace()
    job = create_job(search_space=space)

    class SomeAlgo(SearchAlgorithm):
        def ask(self) -> Optional[List[Experiment]]:
            return None

        def tell(self, experiment: Experiment):
            pass

    with pytest.warns(UserWarning, match="No new configurations."):
        job.do(space, algo_list=[SomeAlgo()])


def test_not_finished_experiment_tell():
    space = SearchSpace()
    job = create_job(search_space=space)

    ex = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        requestor="foo",
        create_timestamp=0.0,
        params={
            "x": 0.0,
            "y": 1.0
        },
    )

    with pytest.raises(ExperimentNotFinishedError):
        job.tell(ex)


def test_job_duplicated_error():
    create_job(search_space=SearchSpace(),
               name="foo",
               storage="sqlite:///foo.db")

    with pytest.raises(DuplicatedJobError):
        create_job(search_space=SearchSpace(),
                   name="foo",
                   storage="sqlite:///foo.db")


def test_load_non_existed():

    with pytest.raises(JobNotFoundError):
        load_job(search_space=SearchSpace(),
                 name="dimple",
                 storage="sqlite:///:memory:")

    with pytest.raises(JobNotFoundError):
        load_job(search_space=SearchSpace(),
                 name="dimple",
                 storage="tinydb:///zoo.json")


def test_load_storage():
    assert isinstance(_load_storage("tinydb:///foo.json"), TinyDBStorage)

    with pytest.raises(InvalidStorageRFC1738):
        _load_storage("dfddsfdsfsd")

    with pytest.raises(InvalidStoragePassed):
        _load_storage(dict(a=1))
