import random
from itertools import tee

import numpy
import numpy as np

from feijoa import SearchSpace, load_job
from feijoa.utils import logging


def pairwise(iterable):
    """
    Generate pairwise of iterable.

    .code-block:

    >>> pairwise('ABCDEFG')
    AB BC CD DE EF FG

    :param iterable: iterable object
    :return: pairwise of iterable.
    """

    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def sigmoid(x, alpha):
    """Sigmoid function"""
    return 1 / (1 + np.exp(-alpha * x))


class Perceptron3:
    def __init__(
        self,
        network_shape: tuple,
        n_epochs: int = 500,
        alpha: float = 1,
        nu: float = 0.2,
        ad: float = 1,
    ):

        self.n_epochs = n_epochs
        self.alpha = alpha
        self.nu = nu
        self.shape = network_shape

        self.err_trend = np.array([])

        self.last_layer_additional = ad
        self._synaptic_weights = None

    @property
    def synaptic_weights(self):
        if not self._synaptic_weights:
            self.randomize_synaptic_weights()
        return self._synaptic_weights

    def randomize_synaptic_weights(self):
        self._synaptic_weights = self._generate_synaptic_weights()

    def _generate_synaptic_weights(self):
        return [
            np.random.random((rows, cols))
            for rows, cols in pairwise(self.shape)
        ]

    @property
    def alpha_regular_layer(self):
        return self.alpha

    @property
    def alpha_last_layer(self):
        return self.alpha_regular_layer + self.last_layer_additional

    @property
    def layers_count(self):
        return len(self.shape) - 1

    # noinspection PyPep8Naming
    def fit(self, X, y):
        """Fit perceptron with stochastic gradient descent.

        Parameters
        ----------

        :param X: Matrix of training data.
        :param y: Target values.
        """

        errors = np.array([])

        for _ in range(self.n_epochs):
            for sample, target in zip(X, y):
                outputs = self._dive(sample)

                total_error = sum(1 / 2 * (target - outputs[-1])**2)
                errors = np.append(errors, total_error)

                d_last_layer = np.array([
                    -2 * self.alpha_last_layer * oj * (1 - oj) * (tj - oj)
                    for oj, tj in zip(outputs[-1], target)
                ])

                # noinspection PyTypeChecker
                ds = [None] * (self.layers_count - 1) + [d_last_layer]
                for i in range(self.layers_count - 2, -1, -1):
                    ds[i] = self._calc_darray_regular(i + 1, outputs[i + 1],
                                                      ds[i + 1])

                adjustments = [
                    self._calc_adjustments_mat(i, outputs[i], ds[i])
                    for i in range(self.layers_count)
                ]

                for i in range(len(self.synaptic_weights)):
                    self.synaptic_weights[i] += adjustments[i]

            self.err_trend = np.append(self.err_trend, sum(errors))
            errors = np.array([])

    def _calc_darray_regular(
        self,
        layer_index: int,
        layer_outputs: numpy.ndarray,
        next_layer_darray: numpy.ndarray,
    ):
        """Generate δ-array for not the last layer."""
        return np.array([
            2 * self.alpha * oj * (1 - oj) *
            sum(dk * self.synaptic_weights[layer_index][j][k]
                for k, dk in enumerate(next_layer_darray))
            for j, oj in enumerate(layer_outputs)
        ])

    def _calc_adjustments_mat(
        self,
        layer_index: int,
        layer_outputs: numpy.ndarray,
        next_layer_darray: numpy.ndarray,
    ):
        """Calculate ΔW matrix for current layer."""
        return np.array([[
            -self.nu * layer_outputs[i] * next_layer_darray[j]
            for j in range(self.synaptic_weights[layer_index].shape[1])
        ] for i in range(self.synaptic_weights[layer_index].shape[0])])

    def _dive(self, x):
        """Get all outputs for current sample."""

        outputs = list()
        cur = x

        for i, sw in enumerate(self.synaptic_weights):
            alpha = (self.alpha_last_layer if i == len(self.synaptic_weights)
                     else self.alpha_regular_layer)

            output = sigmoid(np.dot(cur, sw), alpha)
            outputs.append(output)
            cur = output

        return [x, *outputs]

    # noinspection PyPep8Naming
    def predict(self, x):
        *_, output = self._dive(x)
        return output


def run(h1: int, h2: int, alpha: float):
    clf = Perceptron3((35, h1, h2, 4), alpha=alpha, nu=0.5, ad=10)

    study = [
        np.array([
            1, 1, 1, 1, 1,
            0, 0, 0, 0, 1,
            0, 0, 0, 0, 1,
            0, 0, 0, 1, 0,
            0, 0, 1, 0, 0,
            0, 1, 0, 0, 0,
            1, 0, 0, 0, 0,
        ]),
        np.array([
            1, 1, 1, 1, 1,
            1, 0, 0, 0, 1,
            1, 0, 0, 0, 1,
            1, 1, 1, 1, 1,
            1, 0, 0, 0, 1,
            1, 0, 0, 0, 1,
            1, 1, 1, 1, 1,
        ]),
        np.array([
            1, 1, 1, 1, 1,
            1, 1, 0, 1, 1,
            1, 1, 1, 1, 1,
            0, 0, 1, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 1, 0, 0,
            0, 0, 1, 0, 0,
        ]),
        np.array([
            0, 0, 0, 0, 0,
            0, 0, 0, 0, 0,
            0, 1, 1, 1, 0,
            0, 1, 1, 1, 0,
            1, 1, 1, 1, 1,
            1, 0, 0, 0, 1,
            1, 0, 0, 0, 1,
        ]),
    ]

    q = [
        np.array([1, 0, 0, 0]),
        np.array([0, 1, 0, 0]),
        np.array([0, 0, 1, 0]),
        np.array([0, 0, 0, 1]),
    ]

    clf.fit(study, q)

    prediction = clf.predict(np.array([
        1, 1, 1, 1, 1,
        0, 0, 0, 0, 1,
        0, 0, 0, 0, 1,
        0, 0, 1, 1, 0,
        0, 0, 1, 1, 0,
        0, 1, 0, 0, 0,
        1, 0, 0, 0, 0,
    ]))

    prediction_2 = clf.predict(np.array([
        1, 1, 1, 1, 1,
        1, 1, 0, 1, 1,
        1, 1, 1, 1, 1,
        0, 1, 1, 1, 0,
        0, 1, 1, 1, 0,
        0, 1, 1, 1, 0,
        0, 1, 1, 1, 0,
    ]))

    return sum(1 / 2 * (prediction - np.array([1, 0, 0, 0]))**2) + sum(
        1 / 2 * (prediction_2 - np.array([0, 0, 1, 0]))**2)


doc = """
- signature: h1
  type: integer
  range: [1, 64]

- signature: h2
  type: integer
  range: [1, 64]

- signature: alpha
  type: real
  range: [0.0, 20.0]
"""

logging.init(verbose=True)

log = logging.logging.getLogger(__name__)


def objective(experiment):
    log.info(f"PARAMS: {experiment.params}")
    results = numpy.array([run(**experiment.params) for _ in range(3)])
    log.info(f"RESULTS: {results}")
    mean = results.mean()
    log.info(f"MEAN: {mean}")
    experiment.metrics = {"std": results.std()}
    return mean


def run_training():

    random.seed(10)
    numpy.random.seed(10)

    space = SearchSpace.from_yaml(doc)
    job = load_job(
        name="job14_45_33_04_22_2022",
        search_space=space,
        storage="sqlite:///perceptron.db",
    )

    return job

    # job.do(objective, n_trials=100)
    #
    # return job


if __name__ == "__main__":
    # job =
    print(run_training())
    # fig = px.scatter(x=range(len(clf.err_trend)), y=clf.err_trend)
    # fig.show()
