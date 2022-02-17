from typing import List, Optional

from tinydb import Query, TinyDB
from tinydb.table import Document

from polytune.models import Experiment
from polytune.storages.storage import Storage

__all__ = [
    'TinyDBStorage'
]


class DBVersionException(Exception):
    """Raises if version isn't correct."""


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
                raise DBVersionException()

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
        self.experiments_table.insert(doc)

    def get_experiment_by_id(self, experiment_id):
        q = self.experiments_table.search(Query().id == experiment_id)
        assert len(q) == 1
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
