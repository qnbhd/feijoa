import hashlib
import json

from feijoa import Experiment
from feijoa.models.experiment import ExperimentState


def test_experiment():

    ex1 = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params={"x": 0.0, "y": 1.0},
    )

    print(str(ex1))

    assert (
        str(ex1)
        == """Experiment({
    "id": 0,
    "job_id": 0,
    "state": "WIP",
    "hash": null,
    "objective_result": null,
    "params": {
        "x": 0.0,
        "y": 1.0
    },
    "create_timestamp": 0.0,
    "finish_timestamp": null,
    "metrics": null
})"""
    )

    assert not ex1.is_finished()

    ex1.apply(1.0)
    ex1.success_finish()

    ex1_hash = ex1.hash
    hash_len = len(ex1_hash)

    params_part = ex1_hash[: hash_len // 2]
    objective_part = ex1_hash[hash_len // 2 :]

    params_dumped = json.dumps(ex1.params, sort_keys=True)

    assert (
        hashlib.sha1(params_dumped.encode()).hexdigest()
        == params_part
    )
    assert (
        hashlib.sha1(str(ex1.objective_result).encode()).hexdigest()
        == objective_part
    )

    ex2 = Experiment(
        id=0,
        job_id=0,
        state=ExperimentState.WIP,
        create_timestamp=0.0,
        params={"x": 0.0, "y": 1.0},
    )

    ex2.set_error()
    assert ex2.state == ExperimentState.ERROR

    ex2.error_finish()
    assert ex2.finish_timestamp
