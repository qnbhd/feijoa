from utils import bench, group, iterations


@bench
@group('synthetic')
@iterations(10, 100, 1000)
def f(
        x: '[0, 10]:integer',
        y: '[0.0, 100]:real',
        b: '[foo, bar, zoo]:categorical'
):
    return x ** 2 + y + b
