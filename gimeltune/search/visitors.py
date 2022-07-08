import random

from gimeltune.search.parameters import ParametersVisitor


class Randomizer(ParametersVisitor):
    def visit_integer(self, p):
        return random.randint(p.low, p.high)

    def visit_real(self, p):
        return (p.high - p.low) * random.random() + p.low

    def visit_categorical(self, p):
        return random.choice(p.choices)
