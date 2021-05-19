import pygame
from numpy import random


class Apple:
    def __init__(self, parent_screen, board_size, block_size):
        self.parent_screen = parent_screen
        self.board_size = board_size
        self.block_size = block_size
        self.x = self.board_size[0] // 4
        self.y = self.board_size[1] // 4

    def draw(self):
        block = pygame.Rect(self.x * self.block_size, self.y * self.block_size, self.block_size, self.block_size)
        pygame.draw.rect(self.parent_screen, (255, 0, 0), block)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 2)

    def move(self):
        self.x = random.randint(0, self.board_size[0])
        self.y = random.randint(0, self.board_size[1])

    def move_training(self):
        self.x = random.choice([1, 3]) * self.board_size[0] // 4
        self.y = random.choice([1, 3]) * self.board_size[1] // 4


if __name__ == "__main__":

    pygame.init()
    surface = pygame.display.set_mode((200, 200))
    surface.fill((255, 255, 255))

    apple = Apple(surface, (20, 20), 10)

    for _ in range(10000):
        apple.move()
        apple.draw()
        pygame.display.flip()
