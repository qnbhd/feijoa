import numpy as np
import pytest as pytest
from sklearn.gaussian_process import GaussianProcessRegressor

from feijoa.search.oracles.bayesian import acquisition


@pytest.mark.parametrize(
    "model_cls, kind, expected",
    (
        [
            GaussianProcessRegressor,
            "naive0",
            np.array([0.1, 0.8, 0.3]),
        ],
        [
            GaussianProcessRegressor,
            "ei",
            np.array(
                [3.98942297e-06, 7.00000000e-01, 2.00000000e-01]
            ),
        ],
        [GaussianProcessRegressor, "poi", np.array([0.5, 1.0, 1.0])],
        [
            GaussianProcessRegressor,
            "ucb",
            np.array([0.100025, 0.800025, 0.300025]),
        ],
        [
            GaussianProcessRegressor,
            "ucb",
            np.array([0.100025, 0.800025, 0.300025]),
        ],
        [
            GaussianProcessRegressor,
            "lfbopoi",
            np.array([0.36, 0.95, 0.95]),
        ],
    ),
)
def test_acquisition_function_correct(model_cls, kind, expected):
    X = np.array([[0.1, -5.0, 3.0], [0.6, 0.3, 0.3], [0.6, 0.7, 0.3]])
    y = np.array([0.1, 0.8, 0.3])

    model = model_cls(random_state=0)
    model.fit(X, y)

    result = acquisition(model, kind, X, X, y, random_state=0)

    np.testing.assert_allclose(result, expected)


def test_acquisition_lfbo_weights_update():
    X = np.array([[0.1, -5.0, 3.0], [0.6, 0.3, 0.3], [0.6, 0.7, 0.3]])
    y = np.array([0.1, 0.8, 0.3])

    model = GaussianProcessRegressor(random_state=0)
    model.fit(X, y)

    samples_1 = np.array(
        [[0.1, -5.0, 8.0], [0.6, 0.3, 10.3], [7.6, 0.7, -1.3]]
    )

    result = acquisition(
        model, "lfboei", samples_1, X, y, random_state=0
    )

    np.testing.assert_allclose(
        result, [0.16649222, 0.33968689, 0.40133957]
    )

    X = np.concatenate([X, samples_1])
    y = np.concatenate([y, np.array([0.8, -0.6, 3.8])])

    model.fit(X, y)

    result = acquisition(
        model,
        "lfboei",
        np.array(
            [[0.1, -5.0, 3.0], [0.6, 0.3, 0.3], [0.6, 0.7, 0.3]]
        ),
        X,
        y,
        random_state=0,
    )

    np.testing.assert_allclose(
        result, [0.14623912, 0.43853668, 0.3640345]
    )
