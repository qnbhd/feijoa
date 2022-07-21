from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gimeltune.models import Experiment
from gimeltune.storages.rdb.models import ExperimentModel, JobModel, _Base
from gimeltune.storages.storage import Storage


class RDBStorage(Storage):
    def __init__(self, url):
        self.engine = create_engine(url)
        _Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def insert_job(self, job):
        job_model = JobModel(id=job.id, name=job.name)
        self.session.add(job_model)
        self.session.commit()

    def is_job_name_exists(self, name):
        job_model = self.session.query(JobModel).filter_by(name=name).first()
        return bool(job_model)

    def get_job_id_by_name(self, name) -> Optional[int]:
        job_model = self.session.query(JobModel).filter_by(name=name).first()
        return job_model.id if job_model else None

    def insert_experiment(self, experiment):
        experiment_model = ExperimentModel(
            id=experiment.id,
            job_id=experiment.job_id,
            state=experiment.state,
            hash=experiment.hash,
            objective_result=experiment.objective_result,
            params=experiment.params,
            create_timestamp=experiment.create_timestamp,
            finish_timestamp=experiment.finish_timestamp,
            metrics=experiment.metrics,
        )
        self.session.add(experiment_model)
        self.session.commit()

    def get_experiment(self, job_id, experiment_id):
        experiment_model = (self.session.query(ExperimentModel).filter_by(
            id=experiment_id, job_id=job_id).one())
        return Experiment.from_orm(experiment_model)

    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        experiments_models = (self.session.query(ExperimentModel).filter_by(
            job_id=job_id).all())
        experiments = []
        for exp in experiments_models:
            experiments.append(Experiment.from_orm(exp))
        return experiments

    def get_experiments_count(self, job_id) -> int:
        experiments_models = (self.session.query(ExperimentModel).filter_by(
            job_id=job_id).all())
        return len(experiments_models)

    @property
    def jobs(self):
        jobs_models = self.session.query(JobModel).all()
        jobs = []
        for job_m in jobs_models:
            jobs.append({"id": job_m.id, "name": job_m.name})
        return jobs

    @property
    def version(self):
        raise NotImplementedError()
