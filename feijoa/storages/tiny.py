# MIT License
#
# Copyright (c) 2021 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import List
from typing import NamedTuple
from typing import Optional

from feijoa.utils.imports import ImportWrapper


with ImportWrapper():
    from tinydb import Query, TinyDB
    from tinydb.table import Document

from feijoa.exceptions import DBVersionError
from feijoa.exceptions import InsertExperimentWithTheExistedId
from feijoa.models import Experiment
from feijoa.models.configuration import Configuration
from feijoa.search.space import SearchSpace
from feijoa.storages.storage import Storage


__all__ = ["TinyDBStorage"]


class _Parameter(NamedTuple):
    name: str
    kind: str
    meta: dict


# noinspection PyTypeChecker
class TinyDBStorage(Storage):

    __version__ = "0.1.0"

    def __init__(self, json_file: str):
        self.json_file = json_file
        self.tiny_db = TinyDB(json_file)

        db_version_table = self.tiny_db.table("version")

        if not len(db_version_table.all()):
            # New table
            db_version_table.insert({"version": self.version})
        else:
            ver_record, *_ = db_version_table.all()
            ver = ver_record["version"]
            if ver < self.version:
                raise DBVersionError()

        self.jobs_table = self.tiny_db.table("job")
        self.experiments_table = self.tiny_db.table("experiment")
        self.parameters_table = self.tiny_db.table("parameters")

    def insert_job(self, job):
        doc = {
            "name": job.name,
            "id": job.id,
        }

        self.jobs_table.insert(doc)

        for p in job.search_space:
            name = p.name
            kind = p.__class__.__name__
            meta = p.meta
            param_model = {
                "job_id": job.id,
                "name": name,
                "kind": kind,
                "meta": meta,
            }
            self.parameters_table.insert(param_model)

    def get_search_space_by_job_id(self, job_id) -> SearchSpace:
        parameters = self.parameters_table.search(
            Query().job_id == job_id
        )
        pool = list()
        for p in parameters:
            mod = _Parameter(
                name=p["name"], kind=p["kind"], meta=p["meta"]
            )
            pool.append(mod)
        return SearchSpace.from_db_parameters(pool)

    def get_job_id_by_name(self, name) -> Optional[int]:
        jobs = self.jobs_table.search(Query().name == name)

        if not len(jobs):
            return None

        assert len(jobs) == 1

        job, *_ = jobs

        return job["id"]

    def is_job_name_exists(self, name):
        jobs = self.jobs_table.search(Query().name == name)
        return len(jobs) != 0

    def insert_experiment(self, experiment):
        doc = experiment.dict()
        doc["requestor"] = experiment.params.requestor

        if self.get_experiment(experiment.job_id, experiment.id):
            # TODO (qnbhd): make correct exception
            raise InsertExperimentWithTheExistedId()

        self.experiments_table.insert(doc)

    def get_experiment(self, job_id, experiment_id):
        q = self.experiments_table.search(
            (Query().id == experiment_id) & (Query().job_id == job_id)
        )

        if not q:
            return None

        exp = q[0]
        exp["params"] = Configuration(
            exp["params"], requestor=exp["requestor"]
        )
        exp.pop("requestor")

        return Experiment(**exp)

    def _get_raw_experiments(self, job_id) -> List[Document]:
        docs = self.experiments_table.search(Query().job_id == job_id)
        return docs

    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        docs = self._get_raw_experiments(job_id)
        experiments = []
        for doc in docs:
            doc["params"] = Configuration(
                doc["params"], requestor=doc["requestor"]
            )
            # doc.pop('requestor')
            exp = Experiment(**doc)
            experiments.append(exp)
        return experiments

    def get_experiments_count(self, job) -> int:
        return len(self.get_experiments_by_job_id(job))

    @property
    def jobs(self):
        return self.jobs_table.all()

    @property
    def version(self):
        return self.__version__

    def __del__(self):
        self.tiny_db.close()
