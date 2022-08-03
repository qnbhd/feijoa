import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder

from ..jobs.job import Job
from .evaluator import ImportanceEvaluator


class PCAEvaluator(ImportanceEvaluator):
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
