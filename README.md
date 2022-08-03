<p align="center">
    <img width="600" height="250" src="https://raw.githubusercontent.com/qnbhd/feijoa/349a89b36206a4d1b96036c02657fab247c68307/docs/feijoa_logo.svg">
</p>

<div align="center">

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/feijoa?style=for-the-badge) ![PyPI](https://img.shields.io/pypi/v/feijoa?style=for-the-badge) ![Codecov](https://img.shields.io/codecov/c/github/qnbhd/feijoa?style=for-the-badge)

</div>

Feijoa is a Python framework for hyperparameter's optimization.

The Feijoa API is very easy to use, effective for optimizing machine learning algorithms and various software. Feijoa contains many different use cases.

## Compatibility

Feijoa works with Linux and OS X. Requires Python 3.8 or later.

Feijoa works with [Jupyter notebooks](https://jupyter.org/) with no additional configuration required.

## Installing

Install with `pip` or your favourite PyPI package manager.

```shell
python -m pip install feijoa
```

## Code example

```python
from feijoa import create_job, SearchSpace, Real
from math import sin


def objective(experiment):
    x = experiment.params.get('x')
    y = experiment.params.get('y')

    return sin(x * y)
    
space = SearchSpace()
space.insert(Real('x', low=0.0, high=2.0))
space.insert(Real('y', low=0.0, high=2.0))

job = create_job(search_space=space)
job.do(objective)
```
