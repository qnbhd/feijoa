from fanova import fANOVA
import numpy as np
from sklearn.preprocessing import LabelEncoder

from .evaluator import ImportanceEvaluator


class FanovaEvaluator(ImportanceEvaluator):
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
