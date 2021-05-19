import pygame
from numpy import random
from board_config import BOARD_SIZE, BLOCK_SIZE


class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.x = BOARD_SIZE[0] // 4
        self.y = BOARD_SIZE[1] // 4

    def draw(self):
        block = pygame.Rect(self.x * BLOCK_SIZE, self.y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (255, 0, 0), block)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

    def move(self):
        self.x = random.randint(0, BOARD_SIZE[0])
        self.y = random.randint(0, BOARD_SIZE[1])

    def move_training(self):
        self.x = random.choice([1, 3]) * BOARD_SIZE[0] // 4
        self.y = random.choice([1, 3]) * BOARD_SIZE[1] // 4


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
