from typing import Optional, List

import pytest

from gimeltune import create_job, SearchSpace, Real, Experiment, load_job, SearchAlgorithm
from gimeltune.exceptions import SearchAlgorithmNotFoundedError, ExperimentNotFinishedError, DuplicatedJobError, \
    JobNotFoundError
from gimeltune.models.experiment import ExperimentState


def test_job():
    job = create_job(SearchSpace())

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
    space.insert(Real('x', low=0.0, high=1.0))
    space.insert(Real('y', low=0.0, high=1.0))

    def objective(experiment: Experiment):
        params = experiment.params

        x = params.get('x')
        y = params.get('y')

        return (1 - x) ** 2 + (1 - y) ** 2

    job = create_job(space, 'foo', 'foo')
    job.do(objective, n_trials=10, algo_list=['random'])

    assert isinstance(job.experiments, list) and len(job.experiments) == 10
    assert job.experiments_count == 10
    assert len(job.top_experiments(100)) == 10

    job2 = load_job(SearchSpace(), 'foo', 'foo')

    assert isinstance(job2.experiments, list) and len(job2.experiments) == 10
    assert job2.experiments_count == 10
    assert len(job2.top_experiments(100)) == 10

    print(job2.dataframe)


def test_incorrect_algo_passed():
    space = SearchSpace()
    job = create_job(space)

    with pytest.raises(SearchAlgorithmNotFoundedError):
        job.do(lambda: 1, algo_list=['some_incorrect'])

    class IncorrectAlgo(SearchAlgorithm):
        def ask(self) -> Optional[List[Experiment]]:
            pass

        def tell(self, experiment: Experiment):
            pass

    with pytest.raises(SearchAlgorithmNotFoundedError):
        job.do(lambda: 1, algo_list=[IncorrectAlgo])


def test_no_configurations_warning():
    space = SearchSpace()
    job = create_job(space)

    class SomeAlgo(SearchAlgorithm):
        def ask(self) -> Optional[List[Experiment]]:
            return None

        def tell(self, experiment: Experiment):
            pass

    with pytest.warns(UserWarning, match='No new configurations.'):
        job.do(space, algo_list=[SomeAlgo()])


def test_not_finished_experiment_tell():
    space = SearchSpace()
    job = create_job(space)

    ex = Experiment(
        id=0, job_id=0, state=ExperimentState.WIP,
        requestor='foo', create_timestamp=0.0,
        params={'x': 0.0, 'y': 1.0}
    )

    with pytest.raises(ExperimentNotFinishedError):
        job.tell(ex)


def test_job_duplicated_error():
    create_job(SearchSpace(), 'foo', 'foo')

    with pytest.raises(DuplicatedJobError):
        create_job(SearchSpace(), 'foo', 'foo')


def test_load_non_existed():

    with pytest.raises(JobNotFoundError):
        load_job(SearchSpace(), 'simple', 'dimple')


