from polytune.storages import Storage


class MemoryStorage(Storage):

    def __init__(self):
        super().__init__()
        self.results = dict()
        self.best_cfg = None
        self.hashes = set()

    def insert_hash(self, h):
        self.hashes.add(h)

    def insert_result(self, cfg, result):
        self.results[cfg] = result

        if self.best_cfg is None:
            self.best_cfg = cfg
            return True

        best_result = self.results[self.best_cfg]

        if result < best_result:
            self.best_cfg = cfg
            return True

    def hash_is_exists(self, h):
        return h in self.hashes

    def best_configuration(self):
        return self.best_cfg

    def get_result(self, cfg):
        return self.results.get(cfg, None)
