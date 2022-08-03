import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from ..jobs.job import Job
from .evaluator import ImportanceEvaluator


class MDIEvaluator(ImportanceEvaluator):
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
