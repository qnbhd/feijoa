from typing import Any, Callable, Optional

from polytune.models.configuration import Configuration
from polytune.storages.storage import Storage


Experiment = ...


class Job:

    """
    Facade of framework.
    """

    def __init__(self, name: str, storage: Storage, pruners: Any):
        self.name = name
        self.storage = storage
        self.pruners = pruners
        self.job_id = ...

    @property
    def best_configuration(self) -> Configuration:
        """
        Get the best configuration in job.
        Load configurations with result
        and take best by objective.

        :return: best configuration
        """

        return ...

    @property
    def best_parameters(self) -> dict:
        """
        Get the best parameters in job.
        Load configurations with result
        and take params from best.

        :return: the best parameters' dict.
        """

        return ...

    @property
    def best_value(self) -> float:
        """
        Get the best result value by objective.

        :return: float best value.
        """

        return ...

    @property
    def best_experiment(self) -> Experiment:
        """
        Get the best experiment from job.

        :return: best experiment.
        """

        return ...

    @property
    def configurations(self):
        """
        Load all configurations.
        :return:
        """
        return ...

    @property
    def experiments(self):
        """
        Load all experiments.

        :return:
        """

        return ...

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
        pass

    def do(self, objective: Callable, n_trials: int):
        """

        :param objective:
        :param n_trials:
        :return:
        """
        pass

    def tell(self, experiment: Experiment):
        """
        Finish concrete experiment.

        :return:
        """
        pass

    def ask(self) -> Experiment:
        """

        :return:
        """
        pass

    def export(self, format_: str = ''):
        """

        :param format_:
        :return:
        """
        pass


def load_job(name: str, storage: Storage):
    pass


def create_job(name: str = None, storage: Optional[Storage] = None):
    pass


def job_list(storage: Storage):
    pass

