from typing import Dict, List


def myfunc(fifth: int, sixth: List[str], *args, **kwargs):
    """
    myfunc is a function that takes in two positional arguments and any number of keyword arguments.
    Args:
        fifth (object): fifth argument
        sixth (object): sixth argument
        *args: any number of positional arguments
        **kwargs: keyword arguments

    Returns:

    """
    first = args[0]
    second = args[1]
    third = kwargs.get('third', 0)
    forth = kwargs.get('forth', 0)
    return fifth + sixth + first + second + third + forth


myfunc(1, 2, 3, 4, third=3, forth=4)

try:
    myfunc(1, 2, "t", 4, third=3, forth=4)
except TypeError as e:
    print(e)
except ValueError as e:
    print(e)
    pass
finally:
    print("This is the end of the code")

import numpy as np

names = ["G", "G", "g"]
ages = [25, 30, 35]
person_tuples = [(name, age) for name, age in zip(names, ages)]
print(person_tuples)

print(list(zip(names, ages)))