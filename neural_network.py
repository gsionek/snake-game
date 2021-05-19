# creating a neural network from scratch with the help from:
# https://towardsdatascience.com/how-to-build-your-own-neural-network-from-scratch-in-python-68998a08e4f6

import numpy as np


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))


class NeuralNetwork:
    def __init__(self, architecture, parameters=None):
        self.architecture = architecture
        self.outputs = []

        if parameters is not None:
            self.parameters = parameters
        else:
            # randomize parameters
            self.parameters = {}
            for layer in range(1, len(architecture)):
                key = 'W'+str(layer)
                self.parameters[key] = np.random.uniform(-1, 1, (architecture[layer - 1], architecture[layer]))
                key = 'b'+str(layer)
                self.parameters[key] = np.random.uniform(-1, 1, (1, architecture[layer]))

    def feedforward(self, x):
        self.outputs = []
        for i in range(len(self.architecture) - 1):
            output = sigmoid(np.dot(x, self.parameters['W'+str(i+1)]) + self.parameters['b'+str(i+1)])
            x = output
            self.outputs.append(output)     # save for display


if __name__ == "__main__":
    np.random.seed(2020)
    nn = NeuralNetwork((2, 4, 3))
    X = np.array([[1, 1]])
    nn.feedforward(X)
    for parameter in nn.parameters.keys():
        print('{}: shape {}\t | size {}'.format(
            parameter, nn.parameters[parameter].shape, nn.parameters[parameter].size))
        print(nn.parameters[parameter])

    for y in nn.outputs:
        print('output:')
        print(y)
