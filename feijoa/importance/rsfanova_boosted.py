from collections import defaultdict

import numpy as np
from numpy import float64
from sklearn.preprocessing import LabelEncoder

from .evaluator import ImportanceEvaluator
from ..jobs.job import Job

import rsfanova


class RsFanovaEvaluator(ImportanceEvaluator):

    def do(self, job: Job):
        df = job.get_dataframe(brief=True, only_good=True)
        y = df['objective_result']
        X = df.drop(columns=['objective_result', 'id'])
        categorical = X.select_dtypes(include=['category'])
        encoder = LabelEncoder()

        cols = X.columns

        for cat in categorical.columns:
            X[cat] = encoder.fit_transform(X[cat])

        X = np.array(X, dtype=float64)
        y = np.array(y, dtype=float64)
        X = np.ascontiguousarray(X.transpose())

        importance = rsfanova.fetch_importances(X, y)

        completed = dict()
        completed['parameters'] = cols
        completed['importance'] = np.array(importance)
        return completed

