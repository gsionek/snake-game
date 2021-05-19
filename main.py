import numpy as np
import pygame
import math
from pygame.locals import *
import time
from random import randint
from neural_network import NeuralNetwork
import pickle
from genetic_algorithm import *

BACKGROUND_COLOR = (150, 150, 150)
BLOCK_SIZE = 15
BOARD_SIZE = (20, 20)
WINDOW_SIZE = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)


class GameOver(BaseException):
    pass


class Snake:
    def __init__(self, architecture, parameters, parent_screen, initial_pos, length):
        self.parent_screen = parent_screen
        self.length = length
        self.x = [initial_pos[0]] * length
        self.y = [initial_pos[1]] * length
        self.energy = 60
        self.movements = (-1, 0, 1)        # movements = ('turn left', 'go straight', 'turn right')
        self.directions = ('up', 'right', 'down', 'left')
        self.current_direction_index = 0
        self.current_direction = self.directions[self.current_direction_index]
        self.nn = NeuralNetwork(architecture, parameters)
        self.fitness = 0.0
        self.steps = 0

    def __str__(self):
        return "Snake pos=({}, {})\t e={}\t f={}\t d={}\t   out={}\t ".format(
            self.x[0], self.y[0], self.energy, self.fitness, self.current_direction, self.nn.output)

    def draw(self):
        for i in range(1, self.length):
            block = Rect(self.x[i] * BLOCK_SIZE, self.y[i] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            percentage = (self.length - (i + 1)) / float(self.length)
            minus = 1 - percentage
            pygame.draw.rect(self.parent_screen, (0, 255 * percentage, 255 * minus), block)
            pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

        block = Rect(self.x[0] * BLOCK_SIZE, self.y[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (0, 255, 0), block)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

    def walk(self):
        # update snake's body from tail to head (head excluded)
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # update snake's head
        if self.current_direction == 'up':
            self.y[0] -= 1
        elif self.current_direction == 'down':
            self.y[0] += 1
        elif self.current_direction == 'left':
            self.x[0] -= 1
        elif self.current_direction == 'right':
            self.x[0] += 1

        self.energy -= 1
        self.steps += 1

    def increase(self):
        self.length += 1
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])

    def reset_energy(self):
        self.energy = 60


def is_collision(x0, y0, x1, y1):
    if (x1 == x0) and (y1 == y0):
        return True


def get_distance(x0, y0, x1, y1):
    delta_x = x1 - x0
    delta_y = y1 - y0
    return math.sqrt(delta_x ** 2 + delta_y ** 2)


class Game:
    def __init__(self, architecture, population=100, parameters=None, draw=True, verbose='none'):
        pygame.init()
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        self.surface.fill(BACKGROUND_COLOR)
        self.draw_enabled = draw
        self.print_enabled = verbose
        self.delay = 0.01
        self.paused = False

        self.parameters = parameters
        self.architecture = architecture
        self.snake = self.create_snake(self.architecture, self.parameters[0])
        self.apple = Apple(self.surface)

        self.individuals = []
        self.last_distance = 0
        self.steps_in_good_direction = 0
        self.population = population

    def create_snake(self, architecture, parameter):
        return Snake(architecture, parameter, self.surface, (BOARD_SIZE[0] // 2, BOARD_SIZE[1] // 2), 3)

    def get_next_direction(self):
        input1 = self.apple.x - self.snake.x[0]
        input2 = self.apple.y - self.snake.y[0]
        self.snake.nn.feedforward((input1, input2))
        maximum_index = int(np.argmax(self.snake.nn.output))
        movement = self.snake.movements[maximum_index]
        self.snake.current_direction_index = (self.snake.current_direction_index + movement) % 4
        self.snake.current_direction = self.snake.directions[self.snake.current_direction_index]

    def play(self):
        # move snake:
        self.get_next_direction()
        self.snake.walk()

        # check if snake ran out of energy:
        if self.snake.energy < 0:
            raise GameOver

        # check if snake collides with itself:
        for i in range(3, self.snake.length):
            if is_collision(self.snake.x[0], self.snake.y[0],
                            self.snake.x[i], self.snake.y[i]):
                raise GameOver

        # check if snake is out of board:
        if self.snake.x[0] < 0 or \
                self.snake.x[0] >= BOARD_SIZE[0] or \
                self.snake.y[0] < 0 or \
                self.snake.y[0] >= BOARD_SIZE[1]:
            raise GameOver

        # check if snake collides with apple:
        if is_collision(self.apple.x, self.apple.y, self.snake.x[0], self.snake.y[0]):
            self.snake.fitness += self.snake.energy * 2

            # snake hits maximum length
            if self.snake.length >= BOARD_SIZE[0] * BOARD_SIZE[1]:
                raise GameOver

            # self.snake.increase()
            self.snake.reset_energy()

            # move apple until it is not in a occupied space by the snake
            # TODO: get all available spaces and then choose one of them at random
            apple_in_snake = True
            while apple_in_snake:
                self.apple.move_training()
                apple_in_snake = False
                for i in range(self.snake.length):
                    if is_collision(self.apple.x, self.apple.y, self.snake.x[i], self.snake.y[i]):
                        apple_in_snake = True

        # Calculate fitness:
        distance = get_distance(self.apple.x, self.apple.y, self.snake.x[0], self.snake.y[0])
        if distance < self.last_distance:
            self.steps_in_good_direction += 1
            self.snake.fitness += 1     # * self.steps_in_good_direction
        else:
            self.steps_in_good_direction = 0
            self.snake.fitness -= 1
        self.last_distance = distance

    def draw_background(self):
        self.surface.fill(BACKGROUND_COLOR)
        for i in range(1, BOARD_SIZE[0]):
            x = i * BLOCK_SIZE
            pygame.draw.line(self.surface,
                             color=(200, 200, 200),
                             start_pos=(x, 0),
                             end_pos=(x, WINDOW_SIZE[1]))

        for i in range(1, BOARD_SIZE[1]):
            y = i * BLOCK_SIZE
            pygame.draw.line(self.surface,
                             color=(200, 200, 200),
                             start_pos=(0, y),
                             end_pos=(WINDOW_SIZE[0], y))

    def display_score(self):
        font = pygame.font.SysFont('arial', 20)
        score = font.render("Points: {}".format(self.snake.length),
                            True, (255, 255, 255))
        self.surface.blit(score, (10, 10))

    def draw(self):
        self.draw_background()
        self.snake.draw()
        self.apple.draw()
        # self.display_score()
        pygame.display.flip()
        time.sleep(self.delay)

    def save_individual(self, snake: Snake):
        if self.print_enabled == 'simple' or self.print_enabled == 'detailed':
            print("Individual #{}\t | Score: {}\t | Fitness: {}".format(
                len(self.individuals), self.snake.length, self.snake.fitness))

        individual = {}
        individual['fitness'] = snake.fitness
        individual['score'] = snake.length
        individual['parameters'] = snake.nn.parameters
        self.individuals.append(individual)

    def reset(self):
        self.snake = self.create_snake(self.architecture, self.parameters[len(self.individuals)])
        self.apple = Apple(self.surface)

    def run_one_step(self):
        self.play()
        if self.draw_enabled or (self.population - len(self.individuals)) <= 1:
            self.draw()
        if self.print_enabled == 'detailed':
            print(self.snake)

    def run(self):
        running = True

        # Event Loop:
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:

                    # Esc --> Quit game
                    if event.key == K_ESCAPE:
                        running = False

                    # Enter --> Pause
                    elif event.key == K_RETURN:
                        self.paused = not self.paused

                    # S --> Run step
                    elif event.key == K_s:
                        try:
                            self.run_one_step()
                        except GameOver:
                            self.save_individual(self.snake)
                            self.reset()

                    # R --> Reset individual
                    elif event.key == K_r:
                        self.reset()

                    # K --> Kill individual
                    elif event.key == K_k:
                        self.snake.energy = 0

                    # D --> Draw Enable/Disable
                    elif event.key == K_d:
                        self.draw_enabled = not self.draw_enabled

                    # V --> Print Enable/Disable
                    elif event.key == K_v:
                        if self.print_enabled == 'none':
                            self.print_enabled = 'simple'
                        elif self.print_enabled == 'simple':
                            self.print_enabled = 'detailed'
                        else:
                            self.print_enabled = 'none'

                    # 1 --> Fast Draw Speed
                    elif event.key == K_1:
                        self.delay = 0.01

                    # 2 --> Medium Draw Speed
                    elif event.key == K_2:
                        self.delay = 0.1

                    # 3 --> Slow Draw Speed
                    elif event.key == K_3:
                        self.delay = 1

                elif event.type == QUIT:
                    running = False

            try:
                if not self.paused:
                    self.run_one_step()

            except GameOver:
                self.save_individual(self.snake)
                if len(self.individuals) < self.population:
                    self.reset()
                else:
                    running = False

    def save(self):
        pickle.dump(self.individuals, open('pop.pck', 'wb'))


if __name__ == "__main__":

    population = 500
    nn_architecture = [(2, 4), (4, 3)]
    crossover_rate = 0.7
    mutation_rate = 0.1

    # initial parameters will be chosen at random
    parameters = [None for _ in range(population)]

    # game = Game(population=population, parameters=parameters, draw=True)
    # game.run()
    game = None
    fitness_array = None

    for generation in range(30):

        game = Game(architecture=nn_architecture, population=population, parameters=parameters, draw=False)
        game.run()

        fitness_list = [individual['fitness'] for individual in game.individuals]
        score_list = [individual['score'] for individual in game.individuals]

        fitness_array = np.array(fitness_list)
        score_array = np.array(score_list)

        print('---------------------------------------------')
        print('Generation #{}'.format(generation))

        print('Fitness: Max: {}\t | Min: {}\t | Mean: {}'.format(
            fitness_array.max(), fitness_array.min(), fitness_array.mean()))
        print('Score: Max: {}\t | Min: {}\t | Mean: {}'.format(
            score_array.max(), score_array.min(), score_array.mean()))

        # selecting best individuals for next generation:
        data = game.individuals
        mating_pool = [tournament_selection(data) for _ in range(len(data))]

        mating_fitness = np.array([parent['fitness'] for parent in mating_pool])
        print('Parent Fitness: Max: {}\t | Min: {}\t | Mean: {}'.format(
            mating_fitness.max(), mating_fitness.min(), mating_fitness.mean()))

        parent_chromosomes = [flatten_parameters(parent['parameters']) for parent in mating_pool]
        crossed_chromosomes = []
        for pair in range(0, len(parent_chromosomes), 2):
            for child in crossover(parent_chromosomes[pair], parent_chromosomes[pair + 1], crossover_rate):
                child = mutation(child, mutation_rate)
                crossed_chromosomes.append(child)

        # reshape parameters in the neural network architecture
        children_parameters = []
        for chromosome in crossed_chromosomes:
            children_parameters.append(reshape_parameters(chromosome, nn_architecture))

        parameters = children_parameters

    # save last generation:
    pickle.dump(game.individuals, open('gen_fit_'+str(fitness_array.max()) + '.pck', 'wb'))
    # pickle.dump(game.individuals, open('lower-left.pck', 'wb'))

    print("Game Finished!")

# TODO: Create visualization for Neural Network
# TODO: Create representation of fitness evolution
# TODO: Create Neural Network outside of Snake init
# TODO: Improve network architecture configuration to array of "neurons"
# TODO: Fix style errors
# TODO: Refactor Game and __main__ into different classes/application
# TODO: Make possible to choose and display a selected individual
# TODO: Add seed to random to replicate scenarios
