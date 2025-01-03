import numpy as np


def f0(x):
    """
    SEED = 0xFEBA3209B4C18DA4
    POPULATION_SIZE = 500
    MAX_DEPTH = 5
    MAX_GENERATIONS = 5000
    EARLY_STOP_WINDOW_SIZE = 1000

    xover 30
    point 1
    hoist 2
    permutation 5
    change_exploitation_bias(100, 0.05)
    fine_tune_constants(0.90, EARLY_STOP_WINDOW_SIZE // 4, 1 + 1e-3, 10)
    """
    # return x[0] + (0.2 * np.sin(x[1]))
    return (x[0] + (0.198 * np.sin(x[1]))) + (0.008 * np.sin((0.194 * np.sin(x[1]))))


def f1(x):
    return np.sin(x[0])


def f2(x):
    ...
    # return np.sin(x[0] + x[1])


def f3(x):
    """
    SEED = 0xFEBA3209B4C18DA4
    POPULATION_SIZE = 400
    MAX_DEPTH = 4
    MAX_GENERATIONS = 5000
    EARLY_STOP_WINDOW_SIZE = 2000

    xover 20
    point 1
    hoist 2
    permutation 5
    balance_exploitation(gp, 500, 0.05)
    fine_tune_constants(0.90, EARLY_STOP_WINDOW_SIZE // 4, 1 + 1e-3, 10)
    """
    return 20.363 + ((0.015 - x[1]) * (x[1] * x[1]))


def f4(x):
    """
    SEED = 0xFEBA3209B4C18DA4
    POPULATION_SIZE = 500
    MAX_DEPTH = 4
    MAX_GENERATIONS = 5000
    EARLY_STOP_WINDOW_SIZE = 2000

    xover 20
    point 1
    hoist 2
    permutation 5
    balance_exploitation(gp, 500, 0.05)
    fine_tune_constants(0.90, EARLY_STOP_WINDOW_SIZE // 4, 1 + 1e-3, 10)
    """
    return ((0.938 + np.cos(x[1])) + np.cos(x[1])) / 0.286
