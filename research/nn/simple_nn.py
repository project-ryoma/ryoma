import numpy as np
import math


class SimpleNeuralNetwork:
    """
    A simple neural network built from scratch.
    """

    def __init__(self, input_size: int, layer_size: int):
        """
        Initialize the neural network.
        """
        self.weights = np.random.random([input_size, layer_size])
        self.second_weight = np.random.random(layer_size)
        self.bias = np.random.random(layer_size)
        self.second_bias = np.random.random(layer_size)

    def forward(self, x):
        out = np.dot(x, self.weights) + self.bias
        out = self._relu(out)
        print(out)
        out = np.dot(out, self.second_weight)
        print(out)
        return self._sigmoid(out)

    def backward(self):
        pass

    @staticmethod
    def _relu(x):
        """
        RELU activation function, if v > 0, then x; else 0
        """
        return x * (x > 0)

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-x))


def loss(x, y, model: SimpleNeuralNetwork):
    pred = model.forward(x)
    return - (y * np.log(pred) + (1 - y) * np.log(1 - pred))


x = np.array([
    [1, 0, 3, 4],
    [2, 3, 1, 1],
    [4, 1, 5, 3]
])
y = np.array([1, 0, 0])
nn = SimpleNeuralNetwork(4, 5)
# print(nn.forward(x))

print(loss(x, y, nn))