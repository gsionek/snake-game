# creating a neural network from scratch with the help from:
# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

import numpy as np


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


class NeuralNetwork:
    def __init__(self, architecture, parameters=None):
        # TODO: make NN architecture configurable on init
        if parameters is None:
            self.parameters = {
                'W1': np.random.uniform(-1, 1, architecture[0]),
                'W2': np.random.uniform(-1, 1, architecture[1]),
                'b1': np.random.uniform(-1, 1, (1,  architecture[0][1])),
                'b2': np.random.uniform(-1, 1, (1,  architecture[1][1]))}
        else:
            self.parameters = parameters

        self.layer1 = np.zeros((1, 4))
        self.output = np.zeros((1, 3))

    def feedforward(self, x):
        self.layer1 = sigmoid(np.dot(x, self.parameters['W1']) + self.parameters['b1'])
        self.output = sigmoid(np.dot(self.layer1, self.parameters['W2']) + self.parameters['b2'])


if __name__ == "__main__":
    X = np.array([[1, 1]])

    nn = NeuralNetwork()
    nn.feedforward(X)
    print(nn.parameters['W1'])
    print(nn.parameters['W2'])
    print(nn.layer1)
    print(nn.output)
