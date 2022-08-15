import importlib
import importlib.util
import inspect
import re
import sys

from feijoa import Real, Integer, Categorical, SearchSpace
from pathlib import Path


def bench(func):
    setattr(func, 'for_benchmarking', True)
    return func


def mark(*args, **kwargs):
    def inner(func):
        setattr(func, '__bench_marks__', args)
        setattr(func, '__bench_kw_marks__', kwargs)
        return func
    return inner


def group(group):
    def inner(func):
        setattr(func, '__bench_group__', group)
        return func
    return inner


def iterations(*iters):
    def inner(func):
        setattr(func, '__bench_iterations__', iters)
        return func
    return inner


def get_pool(*pathes):
    funcs = []

    for path in pathes:
        script = Path(path)
        spec = importlib.util.spec_from_file_location(
            script.stem, str(script)
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[module.__name__] = module

        spec.loader.exec_module(module)

        iterable = (
            obj
            for obj in inspect.getmembers(module, inspect.isfunction)
            if (
                obj[1].__module__ == module.__name__
                and getattr(obj[1], 'for_benchmarking', False) and
                obj[1].__name__ not in ['bench', 'iterations', 'group']
            )
        )

        for name, fun in iterable:
            funcs.append(fun)

    return funcs


def pickup_problems(*paths):

    if not paths:
        paths = [
            './simplified.py'
        ]

    problems = list()

    for func in get_pool(*paths):
        space = SearchSpace()

        for key, value in func.__annotations__.items():
            match = re.match("^\[(?P<bounds>.+)]:(?P<kind>.+)", value)
            kind = match.group('kind')
            bounds = match.group('bounds')

            if kind == 'real':
                low, high = map(float, bounds.split(','))
                space.insert(Real(key, low=low, high=high))
            if kind == 'integer':
                low, high = map(int, bounds.split(','))
                space.insert(Integer(key, low=low, high=high))
            if kind == 'categorical':
                choices = list(map(str.strip, bounds.split(',')))
                space.insert(Categorical(key, choices=choices))

        bench_name = func.__name__
        bench_group = getattr(func, '__bench_group__', 'common')
        bench_iterations = getattr(func, '__bench_iterations__', tuple())

        problems.append((func, bench_name, space, bench_group, bench_iterations))

    return problems
