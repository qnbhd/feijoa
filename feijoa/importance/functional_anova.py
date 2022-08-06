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
"""fANOVA importance evaluator module."""

import numpy as np
from sklearn.preprocessing import LabelEncoder

from ..utils.imports import ImportWrapper
from .evaluator import ImportanceEvaluator


with ImportWrapper():
    from fanova import fANOVA


__all__ = ["FanovaEvaluator"]


class FanovaEvaluator(ImportanceEvaluator):
    """fANOVA importance evaluator.

    An Efficient Approach for Assessing Hyperparameter Importance
    https://ml.informatik.uni-freiburg.de/wp-content/uploads/papers/14-ICML-HyperparameterAssessment.pdf

    .. code-block:: python

        from feijoa.importance.functional_anova import FanovaEvaluator

        job = ...
        evaluator = FanovaEvaluator()
        imp = evaluator.do(job)

        params = imp["params"]
        importances = imp["importances"]

    .. note::
        fANOVA is too slow

    See also :class:`~feijoa.importance.rsfanova_boosted.RsFanovaEvaluator`
    """

    # noinspection DuplicatedCode
    def do(self, job):
        df = job.get_dataframe(brief=True, only_good=True)
        y = df["objective_result"]
        X = df.drop(columns=["objective_result", "id"])
        categorical = X.select_dtypes(include=["category"])
        encoder = LabelEncoder()
        for cat in categorical.columns:
            X[cat] = encoder.fit_transform(X[cat])

        fanova = fANOVA(X, y)
        pars = tuple(range(len(X.columns)))
        importance = fanova.quantify_importance(pars)

        ind = [importance[(i,)] for i in range(len(X.columns))]
        importance = [u["individual importance"] for u in ind]

        completed = dict()
        completed["parameters"] = X.columns
        completed["importance"] = np.array(importance)
        return completed
