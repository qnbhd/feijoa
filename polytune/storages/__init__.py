class Storage:

    def insert_hash(self, h):
        raise NotImplementedError()

    def insert_result(self, cfg, result):
        raise NotImplementedError()

    def hash_is_exists(self, h):
        raise NotImplementedError()

    def best_configuration(self):
        raise NotImplementedError()

    def get_result(self, cfg):
        raise NotImplementedError()
