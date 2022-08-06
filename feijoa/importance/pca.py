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
"""PCA importance evaluator module."""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder

from ..jobs.job import Job
from .evaluator import ImportanceEvaluator


__all__ = ["PCAEvaluator"]


# noinspection DuplicatedCode
class PCAEvaluator(ImportanceEvaluator):
    """Principal component analysis (PCA) importance evaluator.

    .. code-block:: python

        from feijoa.importance.pca import PCAEvaluator

        job = ...
        evaluator = PCAEvaluator()
        imp = evaluator.do(job)

        params = imp["params"]
        importances = imp["importances"]
    """

    def __init__(self):
        self.pca = PCA()

    def do(self, job: Job):
        df = job.get_dataframe(brief=True, only_good=True)
        y = df["objective_result"]
        X = df.drop(columns=["objective_result", "id"])
        categorical = X.select_dtypes(include=["category"])
        encoder = LabelEncoder()
        for cat in categorical.columns:
            X[cat] = encoder.fit_transform(X[cat])

        self.pca.fit(X, y)
        importance = np.array(self.pca.explained_variance_)
        completed = dict()
        completed["parameters"] = X.columns
        completed["importance"] = np.array(importance)
        return completed
