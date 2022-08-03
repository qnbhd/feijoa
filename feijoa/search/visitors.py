import random

from feijoa.search.parameters import ParametersVisitor


class Randomizer(ParametersVisitor):
    def __init__(self, seed=0):
        self.random_generator = random.Random(x=seed)

    def visit_integer(self, p):
        return self.random_generator.randint(p.low, p.high)

    def visit_real(self, p):
        return (
            p.high - p.low
        ) * self.random_generator.random() + p.low

    def visit_categorical(self, p):
        return self.random_generator.choice(p.choices)
