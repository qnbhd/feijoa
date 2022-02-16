from polytune.models.experiment import Experiment

NAME = 'rosenbrock'
METRICS = ('x', )


def metric_collector(experiment: Experiment):
    params = experiment.params

    x = params.get('x', 5.0)
    y = params.get('y', 5.0)
    o = params.get('O', '2')

    if o == '2':
        r = -1
    elif o == '1':
        r = -2
    elif o == '3':
        r = -10
    else:
        r = 2

    return {'x': (1-x)**2 + (1-y)**2 + r}