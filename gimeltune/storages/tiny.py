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
from typing import List, Optional

from tinydb import Query, TinyDB
from tinydb.table import Document

from gimeltune.exceptions import DBVersionError
from gimeltune.models import Experiment
from gimeltune.storages.storage import Storage

__all__ = [
    'TinyDBStorage'
]


# noinspection PyTypeChecker
class TinyDBStorage(Storage):

    __version__ = '0.1.0'

    def __init__(self, json_file: str):
        self.json_file = json_file
        self.tiny_db = TinyDB(json_file)

        db_version_table = self.tiny_db.table('version')

        if not len(db_version_table.all()):
            # New table
            db_version_table.insert({'version': self.version})
        else:
            ver_record, *_ = db_version_table.all()
            ver = ver_record['version']
            if ver < self.version:
                raise DBVersionError()

        self.jobs_table = self.tiny_db.table('job')
        self.experiments_table = self.tiny_db.table('experiment')

    def insert_job(self, job):
        doc = {
            'name': job.name,
            'id': job.id,
        }
        self.jobs_table.insert(doc)

    def get_job_id_by_name(self, name) -> Optional[int]:
        jobs = self.jobs_table.search(Query().name == name)

        if not len(jobs):
            return None

        assert len(jobs) == 1

        job, *_ = jobs

        return job['id']

    def is_job_name_exists(self, name):
        jobs = self.jobs_table.search(Query().name == name)
        return len(jobs) != 0

    def insert_experiment(self, experiment):
        doc = experiment.dict()

        if self.get_experiment_by_id(experiment.id):
            # TODO (qnbhd): make correct exception
            raise RuntimeError()

        self.experiments_table.insert(doc)

    def get_experiment_by_id(self, experiment_id):
        q = self.experiments_table.search(Query().id == experiment_id)

        if not q:
            return None

        if len(q) != 1:
            # TODO (qnbhd): make correct exception
            raise RuntimeError()

        exp = q[0]
        return Experiment(**exp)

    def _get_raw_experiments(self, job_id) -> List[Document]:
        docs = self.experiments_table.search(Query().job_id == job_id)
        return docs

    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        docs = self._get_raw_experiments(job_id)
        return [Experiment(**doc) for doc in docs]

    def get_experiments_count(self, job) -> int:
        return len(self.get_experiments_by_job_id(job))

    @property
    def jobs(self):
        return self.jobs_table.all()

    @property
    def version(self):
        return self.__version__
