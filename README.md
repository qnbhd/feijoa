<p align="left">
          <img width="600" height="250" src="https://raw.githubusercontent.com/qnbhd/feijoa/fa3a125e1a46d7206bee55ec0ba6cf4f580c2e68/docs/feijoa_logo.svg">
</p>

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/feijoa?style=for-the-badge) ![PyPI](https://img.shields.io/pypi/v/feijoa?style=for-the-badge) ![Codecov](https://img.shields.io/codecov/c/github/qnbhd/feijoa?style=for-the-badge)

Feijoa is a Python framework for hyperparameter's optimization.

The Feijoa API is very easy to use, effective for optimizing machine learning algorithms and various software. Feijoa contains many different use cases.

## Compatibility

Feijoa works with Linux and OS X. Requires Python 3.8 or later.

Feijoa works with [Jupyter notebooks](https://jupyter.org/) with no additional configuration required.

# Installing

Install with `pip` or your favourite PyPI package manager.

`python -m pip install feijoa`

## Code example:

```python
from feijoa import create_job, Experiment, SearchSpace, Real
from math import sin


def objective(experiment: Experiment):
    x = experiment.params.get('x')
    y = experiment.params.get('y')

    return sin(x * y)
    
space = SearchSpace()
space.insert(Real('x', low=0.0, high=2.0))
space.insert(Real('y', low=0.0, high=2.0))

job = create_job(search_space=space)
job.do(objective)
```

