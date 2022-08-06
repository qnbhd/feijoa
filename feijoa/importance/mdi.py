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
"""MDI importance evaluator module."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from ..jobs.job import Job
from .evaluator import ImportanceEvaluator


__all__ = ["MDIEvaluator"]


# noinspection DuplicatedCode
class MDIEvaluator(ImportanceEvaluator):
    """Mean decrease impurity (MDI) importance evaluator.

    .. code-block:: python

        from feijoa.importance.mdi import MDIEvaluator

        job = ...
        evaluator = MDIEvaluator()
        imp = evaluator.do(job)

        params = imp["params"]
        importances = imp["importances"]

    Args:
        n_trees (int): number of trees in RandomForestRegressor.
        max_depth (int): maximum of trees depth.

    """

    def __init__(self, *, n_trees: int = 64, max_depth: int = 64):
        self.forest = RandomForestRegressor(
            n_estimators=n_trees,
            max_depth=max_depth,
            random_state=0,
        )

    def do(self, job: Job):
        df = job.get_dataframe(brief=True, only_good=True)
        y = df["objective_result"]
        X = df.drop(columns=["objective_result", "id"])
        categorical = X.select_dtypes(include=["category"])
        encoder = LabelEncoder()

        for cat in categorical.columns:
            X[cat] = encoder.fit_transform(X[cat])

        self.forest.fit(X, y)
        importance = np.array(self.forest.feature_importances_)
        completed = dict()
        completed["parameters"] = X.columns
        completed["importance"] = np.array(importance)
        return completed
