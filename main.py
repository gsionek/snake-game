import numpy as np
import pygame
from pygame.locals import *
import time
from random import randint
from neural_network import NeuralNetwork


BACKGROUND_COLOR = (150, 150, 150)
BLOCK_SIZE = 15
BOARD_SIZE = (30, 30)
WINDOW_SIZE = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)


class GameOver(BaseException):
    pass


class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.x = 0
        self.y = 0
        self.move()

    def draw(self):
        apple = Rect(self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (255, 0, 0), apple)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), apple, 2)

    def move(self):
        self.x = randint(0, BOARD_SIZE[0] - 1)
        self.y = randint(0, BOARD_SIZE[1] - 1)


class Snake:
    def __init__(self, parent_screen, initial_pos, length):
        self.parent_screen = parent_screen
        self.length = length
        self.x = [initial_pos[0]] * length
        self.y = [initial_pos[1]] * length
        self.energy = 30
        self.movements = (-1, 0, 1)        # movements = ('turn left', 'go straight', 'turn right')
        self.directions = ('up', 'right', 'down', 'left')
        self.current_direction_index = 0
        self.current_direction = self.directions[self.current_direction_index]
        self.nn = NeuralNetwork()
        self.fitness = 0.0
        self.steps = 0

    def __str__(self):
        return "Snake pos=({}, {})\t dir={}\t nn={}".format(
            self.x[0], self.y[0], self.current_direction, self.nn.output)

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
        self.energy = 100


def is_collision(x0, y0, x, y):
    if (x == x0) and (y == y0):
        return True


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        self.surface.fill(BACKGROUND_COLOR)
        self.snake = Snake(self.surface, (BOARD_SIZE[0] // 2, BOARD_SIZE[1] // 2), 3)
        self.snake.draw()
        self.apple = Apple(self.surface)
        self.apple.draw()
        self.paused = False
        self.individual_count = 1

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
            # snake hits maximum length
            if self.snake.length >= BOARD_SIZE[0] * BOARD_SIZE[1]:
                raise GameOver

            self.snake.increase()
            self.snake.reset_energy()

            # move apple until it is not in a occupied space by the snake
            # TODO: get all available spaces and then choose one of them at random
            apple_in_snake = True
            while apple_in_snake:
                self.apple.move()
                apple_in_snake = False
                for i in range(self.snake.length):
                    if is_collision(self.apple.x, self.apple.y, self.snake.x[i], self.snake.y[i]):
                        apple_in_snake = True

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

    def display_game_over(self):
        print("Game Over")
        self.surface.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont('arial', 30)
        message = font.render("Game Over! Your score was: {}".format(self.snake.length), True, (255, 255, 255))
        self.surface.blit(message, (200, 200))
        message = font.render("Press ENTER to try again.", True, (255, 255, 255))
        self.surface.blit(message, (200, 250))
        pygame.display.flip()

    def draw(self):
        self.draw_background()
        self.snake.draw()
        self.apple.draw()
        # self.display_score()
        pygame.display.flip()
        time.sleep(0.01)

    def reset(self):
        self.paused = False
        self.snake = Snake(self.surface, (BOARD_SIZE[0] // 2, BOARD_SIZE[1] // 2), 3)
        self.individual_count += 1
        self.apple = Apple(self.surface)

    def run(self):
        running = True

        # Event Loop:
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:

                    # Esc --> Quit game
                    if event.key == K_ESCAPE:
                        running = False

                    # Enter --> Reset
                    elif event.key == K_RETURN:
                        self.reset()

                elif event.type == QUIT:
                    running = False

            try:
                if not self.paused:
                    self.play()
                    self.draw()
                    print(self.snake)

            except GameOver:
                print("Individual #{}\t | Score: {}".format(self.individual_count, self.snake.length))
                self.reset()
                # self.paused = True
                # self.display_game_over()


if __name__ == "__main__":
    print("Starting game!")
    game = Game()
    game.run()
    print("Game closed!")
