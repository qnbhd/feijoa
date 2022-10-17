import numpy as np

from utils import bench, group, iterations, solution


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def parabolic_cylinder(
    x: "[0, 10]:real",
    y: "[0.0, 100]:real",
):
    return x**2 + y


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def parabolic_cylinder_noised(
    x: "[-10, 10]:real",
    y: "[-100, 100]:real",
):
    return x**2 + y + np.random.random() * 2


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def parabolic_cylinder_noised(
    x: "[-10, 10]:real",
    y: "[-100, 100]:real",
):
    return x**2 + y + np.random.random() * 2


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def rosenbrock(
    x: "[-100, 100]:real",
    y: "[-100, 100]:real",
):
    return 100 * (y - x) ** 2 + (x - 1) ** 2


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def beale(
    x: "[-100.0, 100.0]:real",
    y: "[-100.0, 100.0]:real",
):
    result = (1.5 - x + x * y) ** 2
    result += (2.25 - x + x * y**2) ** 2
    result += (2.625 - x + x * y**3) ** 2
    return result


@bench
@group("synthetic")
@iterations(100)
@solution(3.0)
def goldstein_price(
    x: "[-2.0, 2.0]:real",
    y: "[-2.0, 2.0]:real",
):
    left = 1 + (x + y + 1) ** 2 * (
        19 - 14 * x + 3 * x**2 - 14 * y + 6 * x * y + 3 * y**2
    )
    right = 30 + (2 * x - 3 * y) ** 2 * (
        18 - 32 * x + 12 * x**2 + 48 * y - 36 * x * y + 27 * y**2
    )
    return left * right


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def butt(
    x: "[-10, 10]:real",
    y: "[-10, 10]:real",
):
    return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def bukin6(
    x: "[-15, -5]:real",
    y: "[-3, 3]:real",
):
    return 100 * np.sqrt(np.abs(y - 0.01 * x * x)) + 0.01 * np.abs(x + 10)


@bench
@group("synthetic")
@iterations(100)
@solution(0.0)
def matias(
    x: "[-10, 10]:real",
    y: "[-10, 10]:real",
):
    return 0.26 * (x**2 + y**2) - 0.48 * x * y
