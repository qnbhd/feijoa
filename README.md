![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gimeltune?style=for-the-badge) ![PyPI](https://img.shields.io/pypi/v/gimeltune?style=for-the-badge) ![Codecov](https://img.shields.io/codecov/c/github/qnbhd/gimeltune?style=for-the-badge)

Gimeltune is a Python framework for hyperparameter's optimization.

The Gimeltune API is very easy to use, effective for optimizing machine learning algorithms and various software. Gimeltune contains many different use cases.

## Compatibility

Gimeltune works with Linux and OS X. Requires Python 3.8 or later.

Gimeltune works with [Jupyter notebooks](https://jupyter.org/) with no additional configuration required.

# Installing

Install with `pip` or your favourite PyPI package manager.

`python -m pip install gimeltune`

## Code example:

```python
from gimeltune import create_job, Experiment, SearchSpace, Real
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

