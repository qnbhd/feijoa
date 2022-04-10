import unittest.mock

import pytest

from gimeltune import TinyDBStorage, Experiment

# noinspection DuplicatedCode
from gimeltune.exceptions import DBVersionError, InsertExperimentWithTheExistedId
from gimeltune.models.experiment import ExperimentState


def test_tiny_db_version_check():
    storage1 = TinyDBStorage('boo.json')
    storage1.close()

    with unittest.mock.patch.object(TinyDBStorage, '__version__', '0.1.1'):
        with pytest.raises(DBVersionError):
            TinyDBStorage('boo.json')


def test_insert_experiment_with_the_same_id():
    storage = TinyDBStorage('woo.json')

    ex = Experiment(
        id=0, job_id=0, state=ExperimentState.WIP,
        requestor='foo', create_timestamp=0.0,
        params={'x': 0.0, 'y': 1.0}
    )

    ex_duplicated = Experiment(
        id=0, job_id=0, state=ExperimentState.WIP,
        requestor='foo', create_timestamp=0.0,
        params={'x': 0.0, 'y': 1.0}
    )

    storage.insert_experiment(ex)

    with pytest.raises(InsertExperimentWithTheExistedId):
        storage.insert_experiment(ex_duplicated)

    assert storage.get_experiment_by_id(1000) is None
