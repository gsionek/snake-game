import pygame
from game import Game
from board_config import *
from genetic_algorithm import *
import time

WINDOW_SIZE = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)


class Display:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(WINDOW_SIZE)

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

    def update(self):
        pygame.display.flip()

class World:
    """"The World class contains a population of 'snake games' and evolves the snakes in each game using genetic
    algorithm."""
    def __init__(self, population=100):
        self.display = Display()
        self.population = population
        self.generation_number = 0
        self.current_generation = self.get_first_generation()

    def get_first_generation(self):
        self.generation_number += 1
        return [Game(self.display.surface, draw_enabled=True) for _ in range(self.population)]

    def get_next_generation(self):
        brains = [game.snake.brain for game in self.current_generation]
        fitness = [game.snake.fitness for game in self.current_generation]

        selected_brains = [tournament_selection(brains, fitness) for _ in range(len(brains))]

        parent_chromosomes = [flatten_parameters(brain) for brain in selected_brains]
        crossed_chromosomes = []
        for pair in range(0, len(parent_chromosomes), 2):
            for child in crossover(parent_chromosomes[pair], parent_chromosomes[pair + 1], crossover_rate):
                child = mutation(child, mutation_rate)
                crossed_chromosomes.append(child)

        # reshape parameters in the neural network architecture
        new_brains = []
        nn_architecture = (2, 4, 4)
        for chromosome in crossed_chromosomes:
            new_brains.append(reshape_parameters(chromosome, nn_architecture))

        return [Game(self.display.surface, brain) for brain in new_brains]

    def run_generation(self):
        there_are_games_running = True
        while there_are_games_running:

            self.display.draw_background()

            there_are_games_running = False
            for game in self.current_generation:
                if not game.game_over:
                    there_are_games_running = True
                    game.play()
                    game.draw()
            self.display.update()
            time.sleep(0.1)

    def print_generation_statistics(self):
        pass


if __name__ == "__main__":
    world = World(100)
    world.run_generation()
