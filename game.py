from snake import Snake
from apple import Apple
from board_config import *
import math


class Game:
    """"Game class contains the Snake and Apple and defines the game rules. It also calculates the information
    for the neural network inputs and updates the fitness of the snake along the game."""
    def __init__(self, parent_screen, brain=None, draw_enabled=False, print_enabled=False):
        self.surface = parent_screen
        self.draw_enabled = draw_enabled
        self.print_enabled = print_enabled

        self.snake = Snake(self.surface, brain, (BOARD_SIZE[0] // 2, BOARD_SIZE[1] // 2))
        self.apple = Apple(self.surface)

        self.last_distance = 0
        self.game_over = False

    def get_inputs(self):
        delta_x = self.apple.x - self.snake.x[0]
        delta_y = self.apple.y - self.snake.y[0]
        return delta_x, delta_y

    def update_fitness(self):
        distance = get_distance(self.apple.x, self.apple.y, self.snake.x[0], self.snake.y[0])
        if distance < self.last_distance:
            self.snake.fitness += 1
        else:
            self.snake.fitness -= 1
        self.last_distance = distance

    def move_apple(self):
        # TODO: get all available spaces and then choose one of them at random
        apple_in_snake = True
        while apple_in_snake:
            self.apple.move()
            apple_in_snake = False
            for i in range(self.snake.length):
                if is_collision(self.apple.x, self.apple.y, self.snake.x[i], self.snake.y[i]):
                    apple_in_snake = True
                    break

    def play(self):
        # move snake:
        inputs = self.get_inputs()
        self.snake.process_inputs(inputs)
        self.snake.move()

        # check if snake ran out of energy:
        if self.snake.energy < 0:
            self.game_over = True

        # check if snake collides with itself:
        for i in range(3, self.snake.length):
            if is_collision(self.snake.x[0], self.snake.y[0],
                            self.snake.x[i], self.snake.y[i]):
                self.game_over = True

        # check if snake is out of board:
        if self.snake.x[0] < 0 or \
                self.snake.x[0] >= BOARD_SIZE[0] or \
                self.snake.y[0] < 0 or \
                self.snake.y[0] >= BOARD_SIZE[1]:
            self.game_over = True

        # check if snake collides with apple:
        if is_collision(self.apple.x, self.apple.y, self.snake.x[0], self.snake.y[0]):

            # increase fitness:
            self.snake.fitness += self.snake.energy * 2

            # snake hits maximum length
            if self.snake.length >= BOARD_SIZE[0] * BOARD_SIZE[1]:
                self.game_over = True

            # self.snake.increase()
            self.snake.reset_energy()
            self.move_apple()

        self.update_fitness()

    def draw(self):
        self.snake.draw()
        self.apple.draw()

    def run(self):
        self.play()
        if self.draw_enabled:
            self.draw()
        if self.print_enabled:
            print(str(self.apple) + '\t |' + str(self.snake))


def is_collision(x0, y0, x1, y1):
    if (x1 == x0) and (y1 == y0):
        return True


def get_distance(x0, y0, x1, y1):
    delta_x = x1 - x0
    delta_y = y1 - y0
    return math.sqrt(delta_x ** 2 + delta_y ** 2)


if __name__ == "__main__":

    import time
    import pygame
    from pygame import locals

    pygame.init()
    window_size = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)
    surface = pygame.display.set_mode(window_size)

    game = Game(surface, True, True)

    running = True
    paused = False

    while running:

        for event in pygame.event.get():

            if event.type == locals.KEYDOWN:
                # Esc --> Quit game
                if event.key == locals.K_ESCAPE:
                    running = False
                # Enter --> Pause
                elif event.key == locals.K_RETURN:
                    paused = not paused
            elif event.type == locals.QUIT:
                running = False

        if not paused:
            game.play()

            if game.game_over:
                game = Game(surface)
                continue

            surface.fill((150, 150, 150))
            game.draw()
            pygame.display.flip()
            time.sleep(0.1)
