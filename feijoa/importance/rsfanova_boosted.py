# MIT License
#
# Copyright (c) 2021-2022 Templin Konstantin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""fANOVA importances evaluator uses Rust
implementation of fANOVA algorithm.
"""

import numpy as np
from numpy import float64
from sklearn.preprocessing import LabelEncoder

from ..jobs.job import Job
from ..utils.imports import ImportWrapper
from .evaluator import ImportanceEvaluator


with ImportWrapper():
    import rsfanova

__all__ = ["RsFanovaEvaluator"]


class RsFanovaEvaluator(ImportanceEvaluator):
    """fANOVA importance evaluator rust implementation
    binding for https://github.com/sile/fanova

    .. note::
        This evaluator is experimental.

    .. code-block:: python

        from feijoa.importance.rsfanova_boosted import (
            RsFanovaEvaluator,
        )

        job = ...
        evaluator = RsFanovaEvaluator()
        imp = evaluator.do(job)

        params = imp["params"]
        importances = imp["importances"]

    """

    def do(self, job: Job):
        df = job.get_dataframe(brief=True, only_good=True)
        y = df["objective_result"]
        X = df.drop(columns=["objective_result", "id"])
        categorical = X.select_dtypes(include=["category"])
        encoder = LabelEncoder()

        cols = X.columns

        for cat in categorical.columns:
            X[cat] = encoder.fit_transform(X[cat])

        X = np.array(X, dtype=float64)
        y = np.array(y, dtype=float64)
        X = np.ascontiguousarray(X.transpose())

        importance = rsfanova.fetch_importances(X, y)

        completed = dict()
        completed["parameters"] = cols
        completed["importance"] = np.array(importance)
        return completed
