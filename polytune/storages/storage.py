class Storage:
    def insert(self, cfg, result):
        raise NotImplementedError()

    def hash_is_exists(self, h):
        raise NotImplementedError()

    def best_configuration(self, objective):
        raise NotImplementedError()

    def get_result(self, cfg):
        raise NotImplementedError()

    def results_list(self):
        raise NotImplementedError()
