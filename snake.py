import pygame
from numpy import random
from board_config import BOARD_SIZE, BLOCK_SIZE
from neural_network import NeuralNetwork


class Snake:
    def __init__(self, parent_screen, initial_pos=(0, 0)):
        self.parent_screen = parent_screen
        self.nn = NeuralNetwork((2, 4, 3))
        self.length = 4
        self.color = tuple(random.randint(0, 255, (1, 3)))

        self.head_pos = [initial_pos[0], initial_pos[1]]
        self.tail_pos = [[initial_pos[0], initial_pos[1]]] * (self.length - 1)
        self.movements = (-1, 0, 1)        # movements = ('turn left', 'go straight', 'turn right')
        self.directions = ('up', 'right', 'down', 'left')
        self.current_direction_index = 1
        self.current_direction = self.directions[self.current_direction_index]

        self.energy = 60
        self.fitness = 0.0
        self.steps = 0

    def __str__(self):
        return "Snake pos={}\t e={}\t f={}\t d={}\t   out={}\t ".format(
            self.head_pos, self.energy, self.fitness, self.current_direction, self.nn.outputs[-1])

    def draw(self):
        # draw tail:
        for i in range(len(self.tail_pos)):
            block = pygame.Rect(self.tail_pos[i][0] * BLOCK_SIZE,
                                self.tail_pos[i][1] * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.parent_screen, self.color, block)
            pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

        # draw head:
        block = pygame.Rect(self.head_pos[0] * BLOCK_SIZE,
                            self.head_pos[1] * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (0, 255, 0), block)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

    def move(self):
        # update snake's body from tail to head (head excluded)
        for i in reversed(range(1, len(self.tail_pos))):
            self.tail_pos[i] = self.tail_pos[i - 1].copy()
        self.tail_pos[0] = self.head_pos.copy()

        # update snake's head
        if self.current_direction == 'up':
            self.head_pos[1] -= 1
        elif self.current_direction == 'down':
            self.head_pos[1] += 1
        elif self.current_direction == 'left':
            self.head_pos[0] -= 1
        elif self.current_direction == 'right':
            self.head_pos[0] += 1

        self.energy -= 1
        self.steps += 1

    def increase(self):
        self.length += 1
        self.tail_pos.append(self.tail_pos[-1].copy())

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

            elif event.type == locals.QUIT:
                running = False

        if not paused:
            new_snake.move()
            surface.fill((255, 255, 255))
            new_snake.draw()
            pygame.display.flip()
            time.sleep(0.5)
