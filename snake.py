import pygame
import numpy as np
from numpy import random
from board_config import BOARD_SIZE, BLOCK_SIZE
from neural_network import NeuralNetwork


class Snake:
    """"Snake class defines the snake movement logic and includes a neural network to calculate the next movement
    based on inputs. It also defines drawing methods."""
    def __init__(self, parent_screen, brain, initial_pos=(0, 0)):
        self.surface = parent_screen
        if brain is None:
            self.brain = NeuralNetwork((2, 4, 4))
        else:
            self.brain = brain
        self.length = 2
        self.color = tuple(random.randint(0, 255, (1, 3)))

        self.x = [initial_pos[0]] * self.length
        self.y = [initial_pos[1]] * self.length

        self.movements = (-1, 0, 1)        # movements = ('turn left', 'go straight', 'turn right')
        self.directions = ('up', 'right', 'down', 'left')
        self.current_direction_index = 1
        self.current_direction = self.directions[self.current_direction_index]

        self.energy = 60
        self.fitness = 0
        self.steps = 0

    def __str__(self):
        return "Snake pos=({},{})\t e={}\t f={}\t d={}\t   out={}\t ".format(
            self.x[0], self.y[0], self.energy, self.fitness, self.current_direction, self.brain.get_output())

    def draw(self):
        # draw tail:
        for i in range(1, self.length):
            block = pygame.Rect(self.x[i] * BLOCK_SIZE, self.y[i] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.surface, self.color, block)
            pygame.draw.rect(self.surface, (0, 0, 0), block, 2)

        # draw head:
        block = pygame.Rect(self.x[0] * BLOCK_SIZE, self.y[0] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.surface, (0, 255, 0), block)
        pygame.draw.rect(self.surface, (0, 0, 0), block, 2)

    def process_inputs(self, inputs):
        output = self.brain.feedforward(inputs)
        maximum_index = int(np.argmax(output))
        self.current_direction = self.directions[maximum_index]

    def move(self):
        # update snake's body from tail to head (head excluded)
        for i in reversed(range(1, self.length)):
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
        self.energy += 60


if __name__ == "__main__":

    import time
    from pygame import locals

    pygame.init()
    window_size = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)
    surface = pygame.display.set_mode(window_size)

    new_snake = Snake(surface, (5, 5))

    running = True
    paused = False
    manual_control = False

    while running:
        for event in pygame.event.get():

            if event.type == locals.KEYDOWN:
                # Esc --> Quit game
                if event.key == locals.K_ESCAPE:
                    running = False
                # Enter --> Pause
                elif event.key == locals.K_RETURN:
                    paused = not paused
                elif event.key == locals.K_UP:
                    new_snake.current_direction = 'up'
                elif event.key == locals.K_RIGHT:
                    new_snake.current_direction = 'right'
                elif event.key == locals.K_DOWN:
                    new_snake.current_direction = 'down'
                elif event.key == locals.K_LEFT:
                    new_snake.current_direction = 'left'
                elif event.key == locals.K_SPACE:
                    new_snake.increase()
                elif event.key == locals.K_BACKSPACE:
                    manual_control = not manual_control
            elif event.type == locals.QUIT:
                running = False

        if not paused:
            if not manual_control:
                new_snake.process_inputs((1, 1))
            new_snake.move()
            surface.fill((255, 255, 255))
            new_snake.draw()
            pygame.display.flip()
            print(new_snake)
            time.sleep(0.5)
