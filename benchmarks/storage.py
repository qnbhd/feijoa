import uuid
from collections import defaultdict
from datetime import datetime
from functools import wraps

import numpy as np
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session

from feijoa import Real, SearchSpace, create_job


def clip_locals(locals_: dict, attrs: list):
    return {key: value for key, value in locals_.items() if key in attrs}


class Base:
    @classmethod
    def mk_from_params(cls, params: dict):
        """
        Make model from dict with params.
        """

        # noinspection PyArgumentList
        return cls(
            **{key: value for key, value in params.items() if key in cls.get_columns()}
        )

    @classmethod
    def get_columns(cls):
        # noinspection PyUnresolvedReferences
        return frozenset(m.key for m in cls.__table__.columns)


_Base: declarative_base = declarative_base(cls=Base)


class Machine(_Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    sys_platform = Column(String)
    architecture = Column(String)
    platform = Column(String)
    processor = Column(String)
    os_release = Column(String)
    total_cpus = Column(Integer)
    physical_cpus = Column(BigInteger)
    ram = Column(BigInteger)
    cpu_freq_min = Column(BigInteger)
    cpu_freq_max = Column(BigInteger)

    UniqueConstraint(
        "name",
        "sys_platform",
        "architecture",
        "platform",
        "processor",
        "os_release",
        "total_cpus",
        "physical_cpus",
        "ram",
        "cpu_freq_min",
        "cpu_freq_max",
    )

    @classmethod
    def is_exists(
        cls,
        session: Session,
        name,
        sys_platform,
        architecture,
        platform,
        processor,
        os_release,
        total_cpus,
        physical_cpus,
        ram,
        cpu_freq_min,
        cpu_freq_max,
    ):
        models = (
            session.query(Machine)
            .filter(
                Machine.name == name,
                Machine.sys_platform == sys_platform,
                Machine.architecture == architecture,
                Machine.platform == platform,
                Machine.processor == processor,
                Machine.os_release == os_release,
                Machine.total_cpus == total_cpus,
                Machine.physical_cpus == physical_cpus,
                Machine.ram == ram,
                Machine.cpu_freq_min == cpu_freq_min,
                Machine.cpu_freq_max == cpu_freq_max,
            )
            .all()
        )

        if len(models) > 1:
            raise Exception()
        elif len(models) == 0:
            cls.mk_from_params(locals())


class Optimizer(_Base):
    __tablename__ = "optimizers"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    kind = Column(String, default="unknown")

    @classmethod
    def fetch_unique(cls, session):
        return frozenset(
            opt.name for opt in session.query(cls).distinct(cls.name).all()
        )

    @classmethod
    def is_exists(cls, session, name):
        return session.query(cls).filter(cls.name == name).scalar()


class Problem(_Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    iterations = Column(BigInteger, nullable=False)
    space_size = Column(BigInteger, nullable=False)
    parameters_count = Column(Integer, nullable=False)
    kind = Column(String, nullable=False)
    noise = Column(String, default="unknown")
    modality = Column(String, default="mixed")
    minima = Column(Float)

    UniqueConstraint("name", "iterations")

    @classmethod
    def fetch_unique(cls, session):
        return frozenset(
            problem.name for problem in session.query(cls).distinct(cls.name).all()
        )

    @classmethod
    def is_exists(cls, session, name, space_size, parameters_count):
        return (
            session.query(cls)
            .filter(
                cls.name == name,
                cls.space_size == space_size,
                cls.parameters_count == parameters_count,
            )
            .scalar()
        )


class Trial(_Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True)

    machine_id = Column(ForeignKey(Machine.id))  # type: ignore
    machine = relationship(Machine, backref="trials")

    optimizer_id = Column(ForeignKey(Optimizer.id))  # type: ignore
    optimizer = relationship(Optimizer, backref="trials")

    problem_id = Column(ForeignKey(Problem.id))  # type: ignore
    problem = relationship(Problem, backref="trials")

    best = Column(Float)
    rss_peak = Column(Float)
    rss_mean = Column(Float)
    time = Column(Float)
    dist = Column(Float)

    rewards = Column(BigInteger)

    UniqueConstraint(
        "optimizer_id",
        "problem_id",
        "machine_id",
    )

    @classmethod
    def is_exists(
        cls,
        session: Session,
        problem_id,
        optimizer_id,
        machine_id,
    ):
        return (
            session.query(cls)
            .filter(
                cls.problem_id == problem_id,
                cls.optimizer_id == optimizer_id,
                cls.machine_id == machine_id,
            )
            .scalar()
        )


class Result(_Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)

    id_in_trial = Column(Integer)

    trial_id = Column(ForeignKey(Trial.id))  # type: ignore
    trial = relationship(Trial, backref="results")

    state = Column(String)

    create_date = Column(DateTime)
    finish_date = Column(DateTime)

    objective_value = Column(Float)

    @classmethod
    def is_exists(cls, session: Session, trial_id, id_in_trial):
        return (
            session.query(cls)
            .filter(
                cls.trial_id == trial_id,
                cls.id_in_trial == id_in_trial,
            )
            .scalar()
        )


class BenchmarksStorage:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

        # noinspection PyUnresolvedReferences
        _Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def put_problem(
        self,
        name,
        space_size,
        parameters_count,
        kind,
        iterations,
        noise=None,
        modality=None,
        minim=None,
    ):

        if not Problem.is_exists(
            self.session,
            name,
            space_size,
            parameters_count,
        ):
            problem = Problem.mk_from_params(locals())
            self.session.add(problem)
            self.session.flush()
            self.session.commit()
            return problem.id

        return (
            self.session.query(Problem)
            .filter(
                Problem.name == name,
                Problem.space_size == space_size,
                Problem.parameters_count == parameters_count,
            )
            .one()
            .id
        )

    def put_optimizer(
        self,
        name,
        kind=None,
    ):
        if not Optimizer.is_exists(self.session, name):
            optimizer = Optimizer.mk_from_params(locals())
            self.session.add(optimizer)
            self.session.flush()
            self.session.commit()
            return optimizer.id

        return self.session.query(Optimizer).filter(Optimizer.name == name).one().id

    def put_trial(
        self,
        machine_id,
        optimizer_id,
        problem_id,
        best,
        rss_peak,
        rss_mean,
        time,
        dist,
        rewards,
    ):
        """
        Insert trial to database.

        Args:
            machine_id (int):
                Machine identifier in database.
            problem_id (int):
                Problem identifier in database.
            optimizer_id (int):
                Optimizer identifier in database.
            best (int):
                Best objective value in specified trial.
            rss_mean (int):
                Resident set size mean value for
                current trial.
            rss_peak (int):
                Resident set size max value for
                current trial.
            time (float):
                Execution time for trial.
            dist (float):
                Distance from best value of trial
                to solution value.
                `dist := |f(best) - f(solution)|`
                This value can be None temporary
                if exact value isn't known.
            rewards (int):
                length of monotonic decreasing subsequence objective results

        """

        if not Trial.is_exists(
            self.session,
            problem_id,
            optimizer_id,
            machine_id,
        ):
            trial = Trial.mk_from_params(locals())
            self.session.add(trial)
            self.session.flush()
            self.session.commit()
            return trial.id

        return (
            self.session.query(Trial)
            .filter(
                Trial.problem_id == problem_id,
                Trial.optimizer_id == optimizer_id,
                Trial.machine_id == machine_id,
            )
            .one()
            .id
        )

    def put_machine(
        self,
        name,
        sys_platform,
        architecture,
        platform,
        processor,
        os_release,
        total_cpus,
        physical_cpus,
        ram,
        cpu_freq_min,
        cpu_freq_max,
    ):

        if not Machine.is_exists(
            self.session,
            **clip_locals(locals(), Machine.get_columns()),
        ):
            machine = Machine.mk_from_params(locals())
            self.session.add(machine)
            self.session.flush()
            self.session.commit()
            return machine.id

        # noinspection DuplicatedCode
        return (
            self.session.query(Machine)
            .filter(
                Machine.name == name,
                Machine.sys_platform == sys_platform,
                Machine.architecture == architecture,
                Machine.platform == platform,
                Machine.processor == processor,
                Machine.os_release == os_release,
                Machine.total_cpus == total_cpus,
                Machine.physical_cpus == physical_cpus,
                Machine.ram == ram,
                Machine.cpu_freq_min == cpu_freq_min,
                Machine.cpu_freq_max == cpu_freq_max,
            )
            .one()
            .id
        )

    def put_results(self, trial_uuid, results):
        pool = []

        for e in results:
            params = dict()
            params["trial_id"] = trial_uuid
            params["create_date"] = datetime.fromtimestamp(e.create_timestamp)
            params["state"] = e.state
            params["finish_date"] = datetime.fromtimestamp(e.finish_timestamp)
            params["objective_value"] = e.objective_result
            params["id_in_trial"] = e.id
            pool.append(Result(**params))

        self.session.bulk_save_objects(pool)
        self.session.flush()
        self.session.commit()

    def fetch_trials(self, *filters):
        query = self.session.query(Trial).join(Problem)

        for filter_ in filters:
            query = filter_(query)

        query_records = query.all()

        trials = defaultdict(list)

        for record in query_records:
            obj = {col: getattr(record, col) for col in record.get_columns()}
            for col, val in obj.items():
                trials[col].append(val)

            trials["optimizer"].append(record.optimizer.name)
            trials["problem"].append(record.problem.name)

        return trials

    def fetch_results(self, *filters):
        query = self.session.query(Result).join(Trial).join(Problem)

        for filter_ in filters:
            query = filter_(query)

        query_records = query.all()

        results = defaultdict(list)

        for record in query_records:
            obj = {col: getattr(record, col) for col in record.get_columns()}
            for col, val in obj.items():
                results[col].append(val)
            results["optimizer"].append(record.trial.optimizer.name)

        return results

    def is_exists_trial(
        self,
        problem_id,
        optimizer_id,
        machine_id,
    ):
        return Trial.is_exists(
            self.session,
            problem_id,
            optimizer_id,
            machine_id,
        )

    def get_unique_problems(self):
        return Problem.fetch_unique(self.session)

    def flush(self, objects=None):
        self.session.flush(objects)

    def commit(self):
        self.session.commit()
