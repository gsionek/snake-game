import pygame
from numpy import random
from board_config import BOARD_SIZE, BLOCK_SIZE


class Apple:
    """"Apple class defines the random apple movement and drawing methods."""
    def __init__(self, parent_screen, seed):
        self.surface = parent_screen
        self.rng = random.default_rng(seed)
        self.x = 0
        self.y = 0
        self.move()

    def __str__(self):
        return "Apple pos=({},{})".format(self.x, self.y)

    def draw(self):
        block = pygame.Rect(self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.surface, (255, 0, 0), block)
        pygame.draw.rect(self.surface, (0, 0, 0), block, 2)

    def move(self):
        self.x = self.rng.integers(0, BOARD_SIZE[0])
        self.y = self.rng.integers(0, BOARD_SIZE[1])

    # def move(self):
    #     self.x = self.rng.choice((1, 7)) * BOARD_SIZE[0] // 8
    #     self.y = self.rng.choice((1, 7)) * BOARD_SIZE[1] // 8


if __name__ == "__main__":

    pygame.init()
    window_size = (BOARD_SIZE[0] * BLOCK_SIZE, BOARD_SIZE[1] * BLOCK_SIZE)
    surface = pygame.display.set_mode(window_size)
    surface.fill((255, 255, 255))

    apple = Apple(surface)

    for _ in range(10000):
        apple.move()
        apple.draw()
        pygame.display.flip()
