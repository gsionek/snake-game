import pickle
import numpy as np
from numpy.random import randint, rand


def tournament_selection(population, number_of_competitors=3):
    # first competitor is taken at random
    best_competitor = randint(len(population))
    for other_competitor in randint(0, len(population), number_of_competitors - 1):
        if population[other_competitor]['fitness'] > population[best_competitor]['fitness']:
            best_competitor = other_competitor
    return population[best_competitor]


# TODO: Research a proper way to do crossover with floating parameters
def crossover(parent_1, parent_2, crossover_rate):
    if rand() < crossover_rate:
        # select crossover point that is not on the end of the string
        crossover_point = randint(1, len(parent_1) - 2)
        # perform crossover
        child_1 = parent_1[:crossover_point] + parent_2[crossover_point:]
        child_2 = parent_2[:crossover_point] + parent_1[crossover_point:]
        print("Crossed at " + str(crossover_point))
    else:
        # no crossover
        child_1 = parent_1.copy()
        child_2 = parent_2.copy()
    return [child_1, child_2]


# TODO: Research a proper way to do mutation with floating parameters
def mutation(chromosome, mutation_rate):
    for parameter in chromosome:
        if rand() < mutation_rate:
            parameter += np.random.uniform(-1, 1, 1)
    return chromosome


def flatten_parameters(parameters):
    vector = []
    for parameter in parameters.keys():
        vector.extend(parameters[parameter].flatten())

    return vector


def reshape_parameters(vector, architecture):
    first = 0
    parameters = {}

    # reshape weights
    for layer in range(len(architecture)):
        elements = architecture[layer][0] * architecture[layer][1]
        last = first + elements
        matrix = np.reshape(vector[first:last], architecture[layer])
        parameters['W'+str(layer+1)] = matrix
        # for next iteration
        first = last

    # reshape biases:
    for layer in range(len(architecture)):
        elements = architecture[layer][1]
        last = first + elements
        matrix = np.reshape(vector[first:last], (1, architecture[layer][1]))
        parameters['b'+str(layer+1)] = matrix
        # for next iteration
        first = last

    return parameters


if __name__ == "__main__":

    nn_architecture = [(2, 4), (4, 3)]

    data = pickle.load(open('pop.pck', 'rb'))

    mating_pool = [tournament_selection(data) for _ in range(len(data))]

    mating_pool = data
    parent_chromosomes = [flatten_parameters(parent['parameters']) for parent in mating_pool]

    crossover_rate = 0.0
    mutation_rate = 0.0
    crossed_chromosomes = []
    for i in range(0, len(parent_chromosomes), 2):
        for child in crossover(parent_chromosomes[i], parent_chromosomes[i+1], crossover_rate):
            child = mutation(child, mutation_rate)
            crossed_chromosomes.append(child)

    children_parameters = []
    for chromosome in crossed_chromosomes:
        children_parameters.append(reshape_parameters(chromosome, nn_architecture))
