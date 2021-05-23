from game import Game
from board_config import *
import genetic_algorithm as ga
import numpy as np
import time
import pygame
from pygame import locals

WINDOW_SIZE = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)


class App:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        self.running = True
        self.paused = False
        self.delay = 0
        self.mutation_rate = 0.3
        self.crossover_rate = 0.7

    def draw_background(self):
        self.surface.fill(BACKGROUND_COLOR)
        for column in range(1, BOARD_SIZE[0]):
            x = column * BLOCK_SIZE
            pygame.draw.line(self.surface,
                             color=(200, 200, 200),
                             start_pos=(x, 0),
                             end_pos=(x, WINDOW_SIZE[1]))

        for row in range(1, BOARD_SIZE[1]):
            y = row * BLOCK_SIZE
            pygame.draw.line(self.surface,
                             color=(200, 200, 200),
                             start_pos=(0, y),
                             end_pos=(WINDOW_SIZE[0], y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == locals.KEYDOWN:
                # Esc --> Quit game
                if event.key == locals.K_ESCAPE:
                    self.running = False
                # Enter --> Pause
                elif event.key == locals.K_RETURN:
                    self.paused = not self.paused
                elif event.key == locals.K_d:
                    self.mutation_rate += 0.1
                    print("mutation_rate = {}".format(self.mutation_rate))
                elif event.key == locals.K_s:
                    self.mutation_rate -= 0.1
                    print("mutation_rate = {}".format(self.mutation_rate))
                elif event.key == locals.K_1:
                    self.delay = 0.01
                elif event.key == locals.K_2:
                    self.delay = 0.1
                elif event.key == locals.K_3:
                    self.delay = 0
            elif event.type == locals.QUIT:
                self.running = False

    def show(self):
        time.sleep(self.delay)
        pygame.display.flip()


class World:
    """"The World class contains a population of 'snake games' and evolves the snakes in each game using genetic
    algorithm."""
    def __init__(self, population=100):
        self.app = App()
        self.population = population
        self.generation_number = 0
        self.current_generation = self.get_first_generation()
        self.fitness_list = []

        # self.crossover_rate = 0.7
        # self.mutation_rate = 0.3

    def get_first_generation(self):
        self.generation_number += 1
        return [Game(self.app.surface, parameters=None, draw_enabled=True) for _ in range(self.population)]

    def create_next_generation(self):
        parameters_list = [game.snake.brain.parameters for game in self.current_generation]

        mating_pool = [ga.tournament_selection(parameters_list, self.fitness_list)
                       for _ in range(len(parameters_list))]

        nn_architecture = self.current_generation[0].snake.brain.architecture
        parent_chromosomes = [ga.flatten_parameters(brain, nn_architecture) for brain in mating_pool]
        crossed_chromosomes = []
        for pair in range(0, len(parent_chromosomes), 2):
            for child in ga.crossover(parent_chromosomes[pair], parent_chromosomes[pair + 1], self.app.crossover_rate):
                child = ga.mutation(child, self.app.mutation_rate)
                crossed_chromosomes.append(child)

        # reshape parameters in the neural network architecture
        new_parameters = []
        for chromosome in crossed_chromosomes:
            new_parameters.append(ga.reshape_parameters(chromosome, nn_architecture))

        self.generation_number += 1
        self.current_generation = [Game(self.app.surface, parameters=parameters, draw_enabled=True)
                                   for parameters in new_parameters]

    def run_generation_parallel(self):
        there_are_games_running = True
        while there_are_games_running and self.app.running:
            self.app.handle_events()
            if not self.app.paused:
                self.app.draw_background()
                there_are_games_running = False
                for ind, game in enumerate(self.current_generation):
                    if not game.game_over:
                        there_are_games_running = True
                        game.play()
                        if ind < 50:        # only draw first 50 snakes
                            game.draw()
                self.app.show()

        # update stats
        self.fitness_list = [game.snake.fitness for game in self.current_generation]

    def run_generation_sequential(self):
        for ind, game in enumerate(self.current_generation):
            while not game.game_over and self.app.running:
                self.app.handle_events()
                if not self.app.paused:
                    game.play()
                    if ind < 5:         # only draw first 5 snakes
                        self.app.draw_background()
                        game.draw()
                        self.app.show()

        # update stats
        self.fitness_list = [game.snake.fitness for game in self.current_generation]

    def print_generation_statistics(self):
        fitness = np.array(self.fitness_list)
        print('Generation #{} | Fitness: Max={} \tMean={} \tMin={}'.format(
            self.generation_number, fitness.max(), fitness.mean(), fitness.min()))


if __name__ == "__main__":

    np.random.seed(0)

    world = World(population=500)

    for _ in range(500):
        world.run_generation_parallel()
        # world.run_generation_sequential()
        world.print_generation_statistics()
        world.create_next_generation()

        if not world.app.running:
            break
