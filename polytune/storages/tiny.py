from tinydb import TinyDB, Query

from polytune.models.configuration import Configuration
from polytune.models.result import Result
from polytune.storages.storage import Storage


class TinyDBStorage(Storage):

    def __init__(self, json_path: str):
        self.tiny_db = TinyDB(json_path)

    def insert(self, configuration: Configuration, result: Result):
        record = {
            'hash': hash(configuration),
            'configuration': configuration.dict(),
            'result': result.dict()
        }
        self.tiny_db.insert(record)

    def hash_is_exists(self, h):
        # noinspection PyTypeChecker
        return bool(self.tiny_db.search(Query().hash == h))

    def best_configuration(self, objective):
        m = float('+inf')
        cfg = None

        for item in self.tiny_db:
            r = Result(**item['result'])
            if objective(r) < m:
                m = objective(r)
                cfg = item['configuration']

        return Configuration(**cfg)

    def get_result(self, cfg: Configuration):
        items = self.tiny_db.search(Query().hash == hash(cfg))
        item = items[0]
        return Result(**item['result'])

    def results_list(self):
        buffer = []

        for item in self.tiny_db:
            configuration = item['configuration']
            result = item['result']

            metrics = {f'metric_{k}': v for k, v in result['metrics'].items()}
            params = {f'param_{k}': v for k, v in configuration['data'].items()}

            prepared = {
                'id': result['id'],
                'timestamp': result['timestamp'],
                **metrics,
                **params
            }
            buffer.append(prepared)

        buffer.sort(key=lambda x: x['timestamp'])
        return buffer
