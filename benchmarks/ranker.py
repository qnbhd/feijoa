from collections import defaultdict
from pprint import pprint

from numba import jit
import numpy as np
from scipy.special import softmax


@jit(cache=True, inline="always")
def calc_angle(results, iters):
    angle = 0.0
    for i in range(1, len(results)):
        delta = results[i - 1] - results[i]
        itersbetween = iters[i] - iters[i - 1]
        angle += delta / itersbetween
    return np.arctan(angle / len(results))


@jit(cache=True, inline="always", nopython=True)
def stardantize_angle(angle):
    return (angle - 0.0001) / (np.pi / 2 - 0.0001)


@jit(cache=True, inline="always", nopython=True)
def norm(y, a=0.0, b=1.0):
    return (b - a) * (y - y.min()) / (y.max() - y.min()) + a


@jit(cache=True, inline="always", nopython=True)
def calc_coeffs(s, t, rho, kappa):
    a = 2 * (rho - 2 * kappa + 1) / t / t
    b = (
        (
            -4 * rho * s
            - rho * t
            + 8 * kappa * s
            + 4 * kappa * t
            - 4 * s
            - 3 * t
        )
        / t
        / t
    )
    c = (
        (
            2 * rho * s * s
            + rho * s * t
            - 4 * kappa * s**2
            - 4 * kappa * s * t
            + 2 * s * s
            + 3 * s * t
            + t * t
        )
        / t
        / t
    )
    return a, b, c


def make_curve(s, t, rho, kappa):
    a, b, c = calc_coeffs(s, t, rho, kappa)

    @jit(nopython=True)
    def curve(x):
        if x < s:
            return 0.0

        if s <= x <= s + t:
            return a * x * x + b * x + c

        if x > t:
            return 1 / (10 * x + 1 / rho - 10 * t)

    curve = np.vectorize(curve)

    return curve


def calc_penalty(
    x0_, xhat_, xfmaxx0_, threshold=0.5, rho=0.8, kappa=0.85
):
    ff = make_curve(xhat_, threshold, rho, kappa)
    return ff(x0_)


@jit(cache=True, nopython=True)
def calc_dist(xstar, xhat, xfmaxstar):
    dist = np.abs(xstar - xhat)
    distmax = np.abs(xhat - xfmaxstar)
    return 1 - (dist - distmax) / (xfmaxstar - xhat)


# @lru_cache(None)
def feijoa_score(
    alpha,
    beta,
    gamma,
    optimizers,
    results_desc_trands,
    iterations,
    solution=None,
    tau=10,
    rho=0.7,
    kappa=0.85,
):
    xfmaxx0 = float("-inf")
    xfmaxstar = float("-inf")
    xfminx0 = float("+inf")
    solution = solution or float("+inf")

    for results in results_desc_trands:
        xfmaxx0 = max(xfmaxx0, results[0])
        xfminx0 = min(xfmaxx0, results[0])
        xfmaxstar = max(xfmaxstar, results[-1])

        solution = min(solution, results[-1])

    xhat = solution

    scores = dict()

    for optimizer, results, iters in zip(
        optimizers, results_desc_trands, iterations
    ):
        angle = calc_angle(results, iters)
        angle = stardantize_angle(angle)
        psi = calc_penalty(
            results[0],
            xfminx0,
            xfmaxx0,
            threshold=tau,
            rho=rho,
            kappa=kappa,
        )
        sigma = calc_dist(results[-1], xhat, xfmaxstar)

        if angle < 0 or psi < 0 or sigma < 0:
            return None

        score = (
            alpha * angle**5
            + beta * psi**3
            + gamma * sigma**0.3
        )

        scores[optimizer] = score

    # print(pd.DataFrame(ddf))

    scores_ = softmax(norm(np.array(list(scores.values()))))

    return dict(zip(optimizers, scores_))


def main():
    optimizers = ["egg", "spam", "foo", "bar"]

    results = [
        [10, 5, 3, 2, 0.5],  # egg
        [80, 33, 20, 0.5],  # spam
        [0.5, 0.2],  # foo
        [1.0, 0.8, 0.0],  # bar
    ]

    iterations = [
        [1, 2, 3, 4, 5],
        [1, 5, 6, 7, 10],
        [1, 2],
        [1, 5, 8],
    ]

    solution = 0.0

    scores = feijoa_score(
        0.4, 0.2, 0.9, optimizers, results, iterations, solution
    )

    pprint(scores)

    import plotly.express as px

    fig = px.bar(x=list(scores.keys()), y=list(scores.values()))
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    fig.show()


if __name__ == "__main__":
    main()
