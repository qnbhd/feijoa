from feijoa import Categorical
from feijoa import Integer
from feijoa import Real
import numpy as np


def transform(sol, search_space):
    configuration = dict()

    for value, param in zip(sol, search_space):
        if isinstance(param, Real):
            configuration[param.name] = value
            continue

        rounded = int(value + (0.5 if value > 0 else -0.5))

        if isinstance(param, Integer):
            configuration[param.name] = rounded
        elif isinstance(param, Categorical):
            configuration[param.name] = param.choices[rounded]

    return configuration


def inverse_transform(configuration: dict, search_space):
    solution = np.zeros((len(configuration),), dtype=np.float64)

    for i, (key, value) in enumerate(configuration.items()):
        param = search_space.get(key)

        if isinstance(param, Real):
            solution[i] = value

        if isinstance(param, Integer):
            solution[i] = value

        if isinstance(param, Categorical):
            index = param.choices.index(value)
            solution[i] = index

    return solution
