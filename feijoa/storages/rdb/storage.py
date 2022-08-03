from typing import List
from typing import Optional

from feijoa.models import Experiment
from feijoa.models.configuration import Configuration
from feijoa.search.space import SearchSpace
from feijoa.storages.rdb.models import _Base
from feijoa.storages.rdb.models import ExperimentModel
from feijoa.storages.rdb.models import JobModel
from feijoa.storages.rdb.models import ParameterModel
from feijoa.storages.rdb.models import SearchSpaceModel
from feijoa.storages.storage import Storage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class RDBStorage(Storage):
    def __init__(self, url):
        self.engine = create_engine(url)
        _Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def insert_job(self, job):
        search_space_model = SearchSpaceModel(id=job.id)
        self.session.add(search_space_model)

        for p in job.search_space:
            name = p.name
            kind = p.__class__.__name__
            meta = p.meta
            param_model = ParameterModel(
                search_space_id=search_space_model.id,
                name=name,
                kind=kind,
                meta=meta,
            )
            self.session.add(param_model)

        job_model = JobModel(
            id=job.id,
            name=job.name,
            search_space_id=search_space_model.id,
        )
        self.session.add(job_model)
        self.session.commit()

    def get_search_space_by_job_id(self, job_id):
        job_model = (
            self.session.query(JobModel).filter_by(id=job_id).one()
        )
        parameters = job_model.search_space.parameters
        return SearchSpace.from_db_parameters(parameters)

    def is_job_name_exists(self, name):
        job_model = (
            self.session.query(JobModel).filter_by(name=name).first()
        )
        return bool(job_model)

    def get_job_id_by_name(self, name) -> Optional[int]:
        job_model = (
            self.session.query(JobModel).filter_by(name=name).first()
        )
        return job_model.id if job_model else None

    def insert_experiment(self, experiment):
        experiment_model = ExperimentModel(
            id=experiment.id,
            job_id=experiment.job_id,
            state=experiment.state,
            hash=experiment.hash,
            objective_result=experiment.objective_result,
            params=experiment.params,
            requestor=experiment.params.requestor,
            create_timestamp=experiment.create_timestamp,
            finish_timestamp=experiment.finish_timestamp,
            metrics=experiment.metrics,
        )
        self.session.add(experiment_model)
        self.session.commit()

    def get_experiment(self, job_id, experiment_id):
        experiment_model = (
            self.session.query(ExperimentModel)
            .filter_by(id=experiment_id, job_id=job_id)
            .one()
        )
        return Experiment.from_orm(experiment_model)

    def get_experiments_by_job_id(self, job_id) -> List[Experiment]:
        experiments_models = (
            self.session.query(ExperimentModel)
            .filter_by(job_id=job_id)
            .all()
        )
        experiments = []
        for exp in experiments_models:
            exp.params = Configuration(
                exp.params, requestor=exp.requestor
            )
            experiments.append(Experiment.from_orm(exp))
        return experiments

    def get_experiments_count(self, job_id) -> int:
        experiments_models = (
            self.session.query(ExperimentModel)
            .filter_by(job_id=job_id)
            .all()
        )
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

    def __del__(self):
        self.session.close()
        self.engine.dispose()
