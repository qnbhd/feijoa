from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from functools import wraps
from time import monotonic_ns
from typing import List
import uuid

from clickhouse_sqlalchemy import engines
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

from feijoa import Experiment


_Base: DeclarativeMeta = declarative_base()


def timed_lru_cache(
    _func=None,
    *,
    seconds: int = 7000,
    maxsize: int = 128,
    typed: bool = False,
):
    """Extension over existing lru_cache with timeout
    :param seconds: timeout value
    :param maxsize: maximum size of the cache
    :param typed: whether different keys for different types of cache keys
    """

    def wrapper_cache(f):
        # create a function wrapped with traditional lru_cache
        f = lru_cache(maxsize=maxsize, typed=typed)(f)
        # convert seconds to nanoseconds to set the expiry time in nanoseconds
        f.delta = seconds * 10**9
        f.expiration = monotonic_ns() + f.delta

        @wraps(
            f
        )  # wraps is used to access the decorated function attributes
        def wrapped_f(*args, **kwargs):
            if monotonic_ns() >= f.expiration:
                # if the current cache expired of the decorated function then
                # clear cache for that function and set a new cache value with new expiration time
                f.cache_clear()
                f.expiration = monotonic_ns() + f.delta
            return f(*args, **kwargs)

        wrapped_f.cache_info = f.cache_info
        wrapped_f.cache_clear = f.cache_clear
        return wrapped_f

    # To allow decorator to be used without arguments
    if _func is None:
        return wrapper_cache
    else:
        return wrapper_cache(_func)


class MachineInfoModel(_Base):
    __tablename__ = "machines"

    uuid = Column(String, primary_key=True, nullable=False)

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

    __table_args__ = (engines.Memory(),)

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


class TrialModel(_Base):  # type: ignore
    __tablename__ = "trials"

    uuid = Column(String, primary_key=True, nullable=False)

    machine_uuid = Column(String, nullable=False)

    optimizer = Column(String)

    problem = Column(String)
    space_size = Column(BigInteger)
    parameters_count = Column(Integer)
    problem_group = Column(String)
    noise = Column(String)
    modality = Column(String)
    minima = Column(Float)

    best = Column(Float)
    rss_peak = Column(Float)
    rss_mean = Column(Float)
    time = Column(Float)
    dist = Column(Float)

    iterations = Column(BigInteger)
    rewards = Column(BigInteger)

    UniqueConstraint(
        "optimizer",
        "problem",
        "machine_id",
        "iterations",
        name="uconstr",
    )

    __table_args__ = (engines.Memory(),)


class Result(_Base):
    __tablename__ = "results"

    uuid = Column(String, primary_key=True, nullable=False)
    trial_uuid = Column(String, nullable=False)

    state = Column(String)
    create_datetime = Column(DateTime)
    finish_datetime = Column(DateTime)

    objective_value = Column(Float)

    __table_args__ = (engines.Memory(),)


class BenchesStorage:
    def __init__(self, url):
        self.engine = create_engine(
            url,
        )
        _Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.session.expire_all()

    def insert_machine(
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
        models = (
            self.session.query(MachineInfoModel)
            .filter(
                MachineInfoModel.name == name,
                MachineInfoModel.sys_platform == sys_platform,
                MachineInfoModel.architecture == architecture,
                MachineInfoModel.platform == platform,
                MachineInfoModel.processor == processor,
                MachineInfoModel.os_release == os_release,
                MachineInfoModel.total_cpus == total_cpus,
                MachineInfoModel.physical_cpus == physical_cpus,
                MachineInfoModel.ram == ram,
                MachineInfoModel.cpu_freq_min == cpu_freq_min,
                MachineInfoModel.cpu_freq_max == cpu_freq_max,
            )
            .all()
        )

        if len(models) > 1:
            raise Exception()
        elif len(models) == 0:
            machine = MachineInfoModel(
                uuid=str(uuid.uuid4()),
                name=name,
                sys_platform=sys_platform,
                architecture=architecture,
                platform=platform,
                processor=processor,
                os_release=os_release,
                total_cpus=total_cpus,
                physical_cpus=physical_cpus,
                ram=ram,
                cpu_freq_min=cpu_freq_min,
                cpu_freq_max=cpu_freq_max,
            )
            self.session.add(machine)
            self.session.flush()
            # self.session.commit()
            return machine.uuid
        elif len(models) == 1:
            return models[0].uuid

    def is_exists_trial(
        self, problem, optimizer, machine_uuid, iterations
    ) -> bool:

        result = self.session.query(TrialModel).filter(
            TrialModel.problem == problem,
            TrialModel.optimizer == optimizer,
            TrialModel.machine_uuid == machine_uuid,
            TrialModel.iterations == iterations,
        )

        return result.scalar()

    def insert_trial(
        self,
        machine_uuid,
        problem,
        optimizer,
        best,
        rss_peak,
        rss_mean,
        iterations,
        time,
        dist,
        rewards,
        space_size,
        parameters_count,
        problem_group,
        noise,
        modality,
        minima,
    ) -> str:

        params = dict(
            uuid=str(uuid.uuid4()),
            space_size=space_size,
            parameters_count=parameters_count,
            problem_group=problem_group,
            noise=noise,
            modality=modality,
            minima=minima,
            machine_uuid=machine_uuid,
            problem=problem,
            optimizer=optimizer,
            best=best,
            rss_peak=rss_peak,
            rss_mean=rss_mean,
            iterations=int(iterations),
            time=time,
            dist=dist,
            rewards=int(rewards),
        )

        self.session.execute(TrialModel.__table__.insert(), params)

        return params["uuid"]

    @timed_lru_cache(seconds=10)
    def get_unique_problems(self):
        records = (
            self.session.query(TrialModel)
            .distinct(TrialModel.problem)
            .all()
        )
        return [r.problem for r in records]

    # @timed_lru_cache(seconds=5)
    def load_trials(self, problem=None, iterations=None):
        if problem and iterations:
            trials = (
                self.session.query(TrialModel)
                .filter_by(problem=problem, iterations=iterations)
                .all()
            )
        elif problem and problem != "all":
            trials = (
                self.session.query(TrialModel)
                .filter_by(problem=problem)
                .all()
            )
        else:
            trials = self.session.query(TrialModel).all()

        data = defaultdict(list)

        for trial in trials:
            data["optimizer"].append(trial.optimizer)
            data["problem"].append(trial.problem)
            data["best"].append(trial.best)
            data["rss_peak"].append(trial.rss_peak)
            data["rss_mean"].append(trial.rss_mean)
            data["iterations"].append(trial.iterations)
            data["time"].append(trial.time)
            data["dist"].append(trial.dist)
            data["rewards"].append(trial.rewards)
            data["machine_uuid"].append(trial.machine_uuid)

        return data

    def insert_results(
        self, trial_uuid, experiments_list: List[Experiment]
    ):

        pool = []

        for e in experiments_list:
            params = dict()
            params["uuid"] = str(uuid.uuid4())
            params["trial_uuid"] = trial_uuid
            params["create_datetime"] = datetime.fromtimestamp(  # type: ignore
                e.create_timestamp
            )
            assert e.finish_timestamp is not None
            params["finish_datetime"] = datetime.fromtimestamp(  # type: ignore
                e.finish_timestamp
            )
            assert e.objective_result is not None
            params["objective_value"] = e.objective_result
            pool.append(params)

        # noinspection PyUnresolvedReferences
        self.session.execute(Result.__table__.insert(), pool)  # type: ignore

    def __del__(self):
        self.session.close()
        self.engine.dispose()
