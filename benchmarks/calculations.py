from collections import defaultdict
from pprint import pprint

from numba import jit
from numba import prange
import numpy as np
from scipy.special import softmax
import swifter


@jit(forceobj=True)
def norm(y, a=0.0, b=1.0):
    return (b - a) * (y - y.min()) / (y.max() - y.min()) + a


def make_ranks(
    dataframe,
    metrics,
    directions,
):
    """
    Calculate ranks as weighted sum.

    Args:
        dataframe (pd.DataFrame):
            Pandas dataframe with trials.
        metrics (list):
            List of target metrics to
            analysis.
        directions (list):
            List of {+1, -1} signs to
            calculations.
                If +1 passed for
                current metric =>
                best is minima else
                maxima.

    """

    return norm(
        np.sum(
            norm(dataframe[metrics[i]])
            * (-1 if directions[i] == "min" else 1)
            for i in prange(len(metrics))
        )
    )


def average_ranks_over_machines(
    df,
):
    optimizers = df["optimizer"].unique()
    avg = {
        "optimizer": np.zeros_like(optimizers),
        "rank": np.zeros_like(optimizers, dtype=np.float64),
    }

    for i in prange(len(optimizers)):
        by_optimizer = df[df["optimizer"] == optimizers[i]]
        mean = by_optimizer["rank"].mean()
        avg["optimizer"][i] = optimizers[i]
        avg["rank"][i] = mean

    avg["rank"] = softmax(avg["rank"])

    return avg


def calculate_general_ranks(
    dataframe,
    problem_name,
    metrics,
    directions,
):
    """
    Calculate general ranks for oracles
    with specified problem.

    Args:
        dataframe (pd.DataFrame):
            Fetched dataframe with trials.
        problem_name (str):
            Specified problem name.
        metrics (list):
            List of target metrics to
            analysis.
        directions (list):
            List of {+1, -1} signs to
            calculations.
                If +1 passed for
                current metric =>
                best is minima else
                maxima.

    """

    ranks = make_ranks(dataframe, metrics, directions)
    dataframe["rank"] = ranks

    avg = average_ranks_over_machines(dataframe)

    return avg
