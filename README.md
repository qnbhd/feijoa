<p align="center">
  <img src="https://github.com/qnbhd/polytune/blob/main/project_logo.png" alt="drawing" width="600" height="300"/>
</p>

## Quick links:
***

a b c d e f g e 

## Introduction:
***

a b c d e f g e 

## Code example:

```python
from polytune import create_job, Experiment, SearchSpace, Real
from math import sin

space = SearchSpace()
space.insert(Real('x', low=0.0, high=2.0))
space.insert(Real('y', low=0.0, high=2.0))


def objective(experiment: Experiment):
    x = experiment.params.get('x')
    y = experiment.params.get('y')

    return sin(x * y)

job = create_job(space)
job.do(objective)


```

## Features:
***

a b c d e f g e 
