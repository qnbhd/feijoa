# import abc
# from math import cos
# from math import e
# from math import exp
# from math import pi
# from math import sin
# from math import sqrt
# from typing import Tuple
#
# import numpy as np
# import problem
# from sklearn.model_selection import cross_val_score
# from sklearn.neighbors import KNeighborsClassifier
#
# import feijoa
# from feijoa import Categorical
# from feijoa import Integer
# from feijoa import Real
# from feijoa import SearchSpace
#
#
# class Synthetic(problem.Problem, metaclass=abc.ABCMeta):
#     @property
#     def n_iterations(self) -> int:
#         return 100
#
#     @property
#     def start_points(self):
#         return np.array([[10.0, 10.0], [5.0, 5.0], [-10.0, 10.0]])
#
#
# class Rosenbrock(Synthetic):
#     @property
#     def name(self) -> str:
#         return "rosenbrock"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-100.0, high=100.0))
#         space.insert(Real("y", low=-100.0, high=100.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return {"x": 1, "y": 1}, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         return 100 * (y - x) ** 2 + (x - 1) ** 2
#
#
# class Rastrigin(Synthetic):
#     @property
#     def name(self) -> str:
#         return "rastrigin"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         for i in range(20):
#             space.insert(Real(f"x_{i}", low=-5.12, high=5.12))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         result = 10 * 20
#
#         for i in range(20):
#             x = experiment.params.get(f"x_{i}")
#             result += x**2 - 10 * np.cos(2 * np.pi * x)
#
#         return result
#
#
# class Sphere(Synthetic):
#     @property
#     def name(self) -> str:
#         return "sphere"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         for i in range(20):
#             space.insert(Real(f"x_{i}", low=-20.0, high=20.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         result = 0
#
#         for i in range(20):
#             x = experiment.params.get(f"x_{i}")
#             result += x**2
#
#         return result
#
#
# class Beale(Synthetic):
#     @property
#     def name(self) -> str:
#         return "beale"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-4.5, high=4.5))
#         space.insert(Real("y", low=-4.5, high=4.5))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return {"x": 3, "y": 0.5}, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         result = (1.5 - x + x * y) ** 2
#         result += (2.25 - x + x * y**2) ** 2
#         result += (2.625 - x + x * y**3) ** 2
#
#         return result
#
#
# class Uni1(Synthetic):
#     @property
#     def name(self) -> str:
#         return "uni1"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-20.0, high=20.0))
#         space.insert(Real("y", low=-20.0, high=20.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         return 0.26 * (x**2 + y**2) - 0.48 * x * y
#
#
# class Uni2(Synthetic):
#     @property
#     def name(self) -> str:
#         return "uni2"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-20.0, high=20.0))
#         space.insert(Real("y", low=-20.0, high=20.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         return (
#             -cos(x) * cos(y) * exp(-((x - pi) ** 2 + (y - pi) ** 2))
#         )
#
#
# class Acley(Synthetic):
#     @property
#     def name(self) -> str:
#         return "ackley"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-20.0, high=20.0))
#         space.insert(Real("y", low=-20.0, high=20.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         return (
#             -20.0 * exp(-0.2 * sqrt(0.5 * (x**2 + y**2)))
#             - exp(0.5 * (cos(2 * pi * x) + cos(2 * pi * y)))
#             + e
#             + 20
#         )
#
#
# class Holder(Synthetic):
#     @property
#     def name(self) -> str:
#         return "holder"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#         space.insert(Real("x", low=-20.0, high=20.0))
#         space.insert(Real("y", low=-20.0, high=20.0))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         x = experiment.params.get("x")
#         y = experiment.params.get("y")
#
#         return -abs(
#             sin(x)
#             * cos(y)
#             * exp(abs(1 - (sqrt(x**2 + y**2) / pi)))
#         )
#
#
# class IrisKNN(Synthetic):
#     def __init__(self):
#         from sklearn.datasets import load_iris
#
#         self.X, self.y = load_iris(return_X_y=True)
#
#     @property
#     def name(self) -> str:
#         return "irisknn"
#
#     @property
#     def space(self) -> feijoa.SearchSpace:
#         space = SearchSpace()
#
#         space.insert(Integer("n_neighbors", low=2, high=30))
#         space.insert(
#             Categorical("weights", choices=["uniform", "distance"])
#         )
#         space.insert(Integer("leaf_size", low=10, high=50))
#         space.insert(Integer("p", low=1, high=5))
#         return space
#
#     @property
#     def solution(self) -> Tuple[dict, float]:
#         return None, 0.0
#
#     def evaluate(self, experiment):
#         params = experiment.params
#
#         clf = KNeighborsClassifier(**params)
#
#         # calc score
#         score = cross_val_score(
#             clf, self.X, self.y, scoring="roc_auc_ovr_weighted"
#         )
#
#         return -score.mean()
