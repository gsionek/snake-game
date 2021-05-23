import numpy as np
from numpy.random import randint, rand


def tournament_selection(parameters, fitness, number_of_competitors=3):
    # first competitor is taken at random
    best_competitor = randint(len(parameters))
    for other_competitor in randint(0, len(parameters), number_of_competitors - 1):
        if fitness[other_competitor] > fitness[best_competitor]:
            best_competitor = other_competitor
    return parameters[best_competitor]


def crossover(parent_1, parent_2, crossover_rate):
    if rand() < crossover_rate:
        # select crossover point that is not on the end of the string
        crossover_point = randint(1, len(parent_1) - 2)
        # perform crossover
        child_1 = parent_1[:crossover_point] + parent_2[crossover_point:]
        child_2 = parent_2[:crossover_point] + parent_1[crossover_point:]
    else:
        # no crossover
        child_1 = parent_1.copy()
        child_2 = parent_2.copy()
    return [child_1, child_2]


def mutation(chromosome, mutation_rate):
    new_chromosome = chromosome.copy()
    for i in range(len(chromosome)):
        if rand() < mutation_rate:
            chromosome[i] += np.random.uniform(-1, 1)
    return chromosome


def flatten_parameters(parameters, architecture):
    vector = []

    # flatten weights
    for layer in range(1, len(architecture)):
        vector.extend(parameters['W' + str(layer)].flatten())

    # flatten biases
    for layer in range(1, len(architecture)):
        vector.extend(parameters['b' + str(layer)].flatten())

    return vector


def reshape_parameters(vector, architecture):
    first = 0
    parameters = {}

    # reshape weights
    for layer in range(len(architecture) - 1):
        elements = architecture[layer] * architecture[layer + 1]
        last = first + elements
        matrix = np.reshape(vector[first:last], (architecture[layer], architecture[layer + 1]))
        parameters['W'+str(layer+1)] = matrix
        # for next iteration
        first = last

    # reshape biases:
    for layer in range(len(architecture) - 1):
        elements = architecture[layer+1]
        last = first + elements
        matrix = np.reshape(vector[first:last], (1, architecture[layer+1]))
        parameters['b'+str(layer+1)] = matrix
        # for next iteration
        first = last

    return parameters


if __name__ == "__main__":

    from snake import Snake

    nn_architecture = (2, 4, 3)
    snakes = [Snake(None, None, nn_architecture) for _ in range(2)]

    crossover_rate = 0.0
    mutation_rate = 0.0

    parameters_list = [snake.brain.parameters for snake in snakes]
    fitness_list = [1, 2]
    mating_pool = [tournament_selection(parameters_list, fitness_list)
                   for _ in range(len(parameters_list))]

    parent_chromosomes = [flatten_parameters(brain, nn_architecture) for brain in mating_pool]
    crossed_chromosomes = []
    for pair in range(0, len(parent_chromosomes), 2):
        for child in crossover(parent_chromosomes[pair], parent_chromosomes[pair + 1], crossover_rate):
            child = mutation(child, mutation_rate)
            crossed_chromosomes.append(child)

    # reshape parameters in the neural network architecture
    new_parameters = []
    for chromosome in crossed_chromosomes:
        new_parameters.append(reshape_parameters(chromosome, nn_architecture))

    print('done')