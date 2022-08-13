from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, BigInteger
from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlalchemy import types
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


_Base: DeclarativeMeta = declarative_base()


class MachineInfoModel(_Base):
    __tablename__ = "machine"

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


class TrialModel(_Base):  # type: ignore
    __tablename__ = "trial"

    id = Column(Integer, primary_key=True)

    machine_id = Column(ForeignKey(MachineInfoModel.id))
    machine = relationship(MachineInfoModel, backref="trials")

    optimizer = Column(String)
    problem = Column(String)
    best = Column(Float)
    mem_peak = Column(Float)
    mem_mean = Column(Float)
    time = Column(Float)
    dist = Column(Float)

    iterations = Column(BigInteger)
    iterations_before_best = Column(BigInteger)
    pareto_ranking = Column(BigInteger)

    UniqueConstraint(
        "optimizer",
        "problem",
        "machine_id",
        "iterations",
        name="uconstr",
    )


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
            self.session.commit()
            return machine.id
        elif len(models) == 1:
            return models[0].id

    def is_exists_trial(
        self, problem, optimizer, machine_id, iterations
    ) -> bool:
        result = self.session.query(TrialModel).filter(
            TrialModel.problem == problem,
            TrialModel.optimizer == optimizer,
            TrialModel.machine_id == machine_id,
            TrialModel.iterations == iterations,
        )

        return result.scalar()

    def insert_trial(
        self,
        machine_id,
        problem,
        optimizer,
        best,
        mem_peak,
        mem_mean,
        iterations,
        time,
        dist,
        iterations_before_best,
    ) -> int:

        trial = TrialModel(
            machine_id=machine_id,
            problem=problem,
            optimizer=optimizer,
            best=best,
            mem_peak=mem_peak,
            mem_mean=mem_mean,
            iterations=int(iterations),
            time=time,
            dist=dist,
            iterations_before_best=int(iterations_before_best),
        )

        self.session.add(trial)
        self.session.commit()

        return trial.id

    def set_pareto_ranking(self, trial_id, pareto_rank):
        trial = (
            self.session.query(TrialModel)
            .filter_by(id=trial_id)
            .one()
        )
        trial.pareto_ranking = int(pareto_rank)

        self.session.commit()

    def load_trials(self):
        trials = self.session.query(TrialModel).all()

        data = {
            "optimizer": [],
            "problem": [],
            "best": [],
            "mem_peak": [],
            "mem_mean": [],
            "iterations": [],
            "time": [],
            "dist": [],
            "iterations_before_best": [],
            "pareto_ranking": [],
        }

        for trial in trials:
            data["optimizer"].append(trial.optimizer)
            data["problem"].append(trial.problem)
            data["best"].append(trial.best)
            data["mem_peak"].append(trial.mem_peak)
            data["mem_mean"].append(trial.mem_mean)
            data["iterations"].append(trial.iterations)
            data["time"].append(trial.time)
            data["dist"].append(trial.dist)
            data["iterations_before_best"].append(
                trial.iterations_before_best
            )
            data["pareto_ranking"].append(trial.pareto_ranking)

        return data

    def get_total_ranking(self):
        ranking = self.session.execute(
            r"select optimizer, AVG(pareto_ranking) as ranking from trial group by optimizer;"
        ).all()

        result = {
            "optimizer": [],
            "ranking": [],
        }

        for record in ranking:
            result["optimizer"].append(record.optimizer)
            result["ranking"].append(1 / record.ranking)

        return result
