import random
import warnings
from multiprocessing import Pool
from typing import Any, Callable, Optional, List, Union

from polytune.models.experiment import Experiment, ExperimentsFactory
from polytune.search.searcher import Searcher
from polytune.search.space import SearchSpace
from polytune.storages.storage import Storage, StorageV2
from polytune.storages.tiny import TinyDBStorageV2


class Job:

    """
    Facade of framework.
    """

    def __init__(self, name: str, storage: StorageV2,
                 search_space: SearchSpace, job_id: int,
                 pruners: Any = None):

        self.name = name
        self.storage = storage
        self.pruners = pruners
        self.job_id = job_id

        self.experiments_factory = ExperimentsFactory(self)
        self.optimizer = Searcher(search_space, self.experiments_factory)

        if not self.storage.is_job_name_exists(self.name):
            self.storage.insert_job(self)

    @property
    def best_parameters(self) -> Optional[dict]:
        """
        Get the best parameters in job.
        Load configurations with result
        and take params from best.

        :return: the best parameters' dict.
        """

        return self.best_experiment.params

    @property
    def best_value(self) -> Optional[Any]:
        """
        Get the best result value by objective.

        :return: float best value.
        """

        return self.best_experiment.metrics

    @property
    def best_experiment(self) -> Optional[Experiment]:
        """
        Get the best experiment from job.

        :return: best experiment.
        """

        return self.storage.best_experiment(self.job_id)

    @property
    def experiments(self):
        """
        Load all experiments.

        :return:
        """

        return self.storage.get_experiments_by_job_id(self.job_id)

    @property
    def experiments_count(self):
        """

        :return:
        """

        return self.storage.get_experiments_count(self.job_id)

    def get_configurations(self):
        """

        :return:
        """
        pass

    def top_configurations(self, n: int):
        """

        :param n:
        :return:
        """
        return self.storage.top_experiments(self.job_id, n)

    def do(self, metric_collector: Callable, objective: Callable, n_trials: int = 100):
        """

        :param metric_collector:
        :param objective:
        :param n_trials:
        :return:
        """

        n_proc = 1
        # noinspection PyPep8Naming

        for it in range(n_trials):

            configurations = self.ask()

            with Pool(n_proc) as p:
                metrics_list = p.map(metric_collector, configurations)

            for experiment, metrics in zip(configurations, metrics_list):
                experiment.metrics = metrics
                experiment.objective_result = objective(experiment)
                experiment.success_finish()

                self.tell(experiment)
                self.storage.insert_experiment(experiment)
                print(experiment)

    def tell(self, experiment: Experiment):
        """
        Finish concrete experiment.

        :return:
        """

        if experiment.is_ok():
            self.optimizer.tell(experiment)
            return

        # TODO (qnbhd): refine exception type
        raise Exception()

    def ask(self) -> Optional[List[Experiment]]:
        """

        :return:
        """

        return self.optimizer.ask()

    def export(self, format_: str = ''):
        """

        :param format_:
        :return:
        """
        pass


def create_job(search_space: SearchSpace, name: str = None,
               storage: Union[str, Optional[Storage]] = None):

    """

    :param search_space:
    :param name:
    :param storage:
    :return:
    """

    name = name or f'test_job_{random.randint(0, 9999)}'

    if not storage:
        storage = TinyDBStorageV2(f'{name}.json')
    else:
        if isinstance(storage, str):
            storage = TinyDBStorageV2(f'{storage}.json')

    assert isinstance(name, str)
    assert isinstance(search_space, SearchSpace)
    assert issubclass(type(storage), StorageV2)

    if storage.is_job_name_exists(name):
        # TODO (qnbhd): refine exception type
        raise Exception()

    return Job(name, storage, search_space, storage.jobs_count + 1)


def load_job(search_space: SearchSpace, name: str,
             storage: Union[str, StorageV2]):

    """

    :param search_space:
    :param name:
    :param storage:
    :return:
    """

    if isinstance(storage, str):
        storage = TinyDBStorageV2(f'{storage}.json')

    job_id = storage.get_job_id_by_name(name)

    if not job_id:
        # TODO (qnbhd): refine exception type
        raise Exception()

    experiments = storage.get_experiments_by_job_id(job_id)

    job = Job(name, storage, search_space, job_id)

    for experiment in experiments:
        job.tell(experiment)

    return job
