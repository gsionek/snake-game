# creating a neural network from scratch with the help from:
# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

import numpy as np


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


class NeuralNetwork:
    def __init__(self):
        # TODO: make parameters a dictionary
        self.weights1 = np.random.uniform(-1, 1, (2, 4))
        self.weights2 = np.random.uniform(-1, 1, (4, 3))
        self.bias1 = np.random.uniform(-1, 1, (1, 4))
        self.bias2 = np.random.uniform(-1, 1, (1, 3))

        self.layer1 = np.zeros((1, 4))
        self.output = np.zeros((1, 3))

    def feedforward(self, x):
        self.layer1 = sigmoid(np.dot(x, self.weights1)) + self.bias1
        self.output = sigmoid(np.dot(self.layer1, self.weights2)) + self.bias2


if __name__ == "__main__":
    X = np.array([[1, 1]])

    nn = NeuralNetwork()
    nn.feedforward(X)
    print(nn.weights1)
    print(nn.weights2)
    print(nn.layer1)
    print(nn.output)
