import datetime
from typing import Dict, Union, Any, Optional

from pydantic import BaseModel


class MetricNotExists(Exception):
    """Raises if metric not in result"""


class Result(BaseModel):
    id: int
    timestamp: float
    metrics: Dict[str, Any]
    state: str

    @classmethod
    def get(cls, metrics):
        idx = getattr(cls, 'idx', 0)

        state = 'OK' if all(bool(v) for v in metrics.values()) else 'ERROR'

        metrics = metrics or dict()

        time = datetime.datetime.now()
        timestamp = datetime.datetime.timestamp(time)

        instance = cls(id=idx, timestamp=timestamp,
                       metrics=metrics, state=state)

        setattr(cls, 'idx', idx + 1)
        return instance

    def __repr__(self):
        metrics = {m: (round(v, 3) if v else v) for m, v in self.metrics.items()}
        timestamp = datetime.datetime.fromtimestamp(self.timestamp)
        timestamp = timestamp.strftime('<%m/%d/%Y %H:%M:%S>')

        return f'Result(id={self.id}, timestamp={timestamp},' \
               f' metrics={metrics}, state={self.state})'

    def __str__(self):
        return self.__repr__()

    @property
    def time(self):
        return self.metrics['time']

    def compare(self, objective, other: 'Result'):
        return objective.compare(self, other)

    def get_metric(self, metric_name: str):
        try:
            result = self.metrics.get(metric_name, None)
        except KeyError:
            raise MetricNotExists

        return result

    def __getitem__(self, item):
        return self.get_metric(item)
