import numpy

from polytune.convergence.plugin import ConvergencePlugin
from polytune.models.configuration import Configuration
from polytune.models.result import Result


class ImpactsHistoryPlugin(ConvergencePlugin):

    reason = 'Small impact in last half of results.'

    def __init__(self):
        self.impacts_history = numpy.array([])
        self.last_result = None
        self.threshold = 0.005

    def on_new_best_result(self, configuration: Configuration, result: Result):
        if self.last_result:
            impact = (self.last_result - result.time) / result.time
            print(self.last_result, result.time, impact)
            self.impacts_history = numpy.append(self.impacts_history, impact)

        self.last_result = result.time

    def converged(self):
        length = len(self.impacts_history)
        chunk = self.impacts_history[length//2:]
        print(self.impacts_history)
        print(chunk)
        if len(chunk):
            return chunk.mean() < self.threshold

        return False
