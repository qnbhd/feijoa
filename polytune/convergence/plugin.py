class ConvergencePlugin:

    reason = ''

    def on_new_best_result(self, configuration, result):
        raise NotImplementedError()

    def converged(self):
        raise NotImplementedError()
