from typing import Dict

from polytune.models.result import Result
from polytune.storages import Storage
from numpy import float64
from polytune.models.configuration import Configuration


class MemoryStorage(Storage):
    def __init__(self):
        super().__init__()
        self.results: Dict[Configuration, Result] = dict()
        self.best_cfg = None
        self.hashes = set()

    def insert_hash(self, h: str) -> None:
        self.hashes.add(h)

    def insert_result(self, cfg: Configuration, result: float64) -> bool:
        self.results[cfg] = result

        if self.best_cfg is None:
            self.best_cfg = cfg
            return True

        best_result = self.results[self.best_cfg]

        if result < best_result:
            self.best_cfg = cfg
            return True

    def hash_is_exists(self, h: str) -> bool:
        return h in self.hashes

    def best_configuration(self) -> Configuration:
        return self.best_cfg

    def get_result(self, cfg: Configuration) -> Result:
        return self.results.get(cfg, None)

    def results_list(self):
        buffer = []

        for configuration, result in self.results.items():
            prepared = {
                'id': result.idx,
                'time': result.time,
                'timestamp': result.timestamp,
                **configuration.data
            }
            buffer.append(prepared)

        buffer.sort(key=lambda x: x['timestamp'])
        return buffer
