
import pygame
from pygame.locals import *
import time
from random import randint


BACKGROUND_COLOR = (150, 150, 150)
BLOCK_SIZE = 40
HORIZONTAL_SPACES = 15
VERTICAL_SPACES = 15
WINDOW_SIZE = (HORIZONTAL_SPACES * BLOCK_SIZE, VERTICAL_SPACES * BLOCK_SIZE)


class GameOver(BaseException):
    pass


class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.x = 0
        self.y = 0
        self.move()

    def draw(self):
        apple = Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (255, 0, 0), apple)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), apple, 3)

    def move(self):
        self.x = randint(0, HORIZONTAL_SPACES - 1) * BLOCK_SIZE
        self.y = randint(0, VERTICAL_SPACES - 1) * BLOCK_SIZE


class Snake:
    def __init__(self, parent_screen, length):
        self.parent_screen = parent_screen
        self.length = length
        self.x = [0] * length
        self.y = [0] * length
        self.direction = 'right'
        self.next_direction = 'right'

    def draw(self):
        for i in range(1, self.length):
            block = Rect(self.x[i], self.y[i], BLOCK_SIZE, BLOCK_SIZE)
            percentage = (self.length - (i + 1)) / float(self.length)
            minus = 1 - percentage
            pygame.draw.rect(self.parent_screen, (0, 255 * percentage, 255 * minus), block)
            pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 3)

        block = Rect(self.x[0], self.y[0], BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.parent_screen, (0, 255, 0), block)
        pygame.draw.rect(self.parent_screen, (0, 0, 0), block, 3)

    def move_up(self):
        if self.direction != 'down':
            self.next_direction = 'up'

    def move_down(self):
        if self.direction != 'up':
            self.next_direction = 'down'

    def move_left(self):
        if self.direction != 'right':
            self.next_direction = 'left'

    def move_right(self):
        if self.direction != 'left':
            self.next_direction = 'right'

    def walk(self):
        # update snake's body
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # lock the new direction:
        self.direction = self.next_direction

        # update snake's head
        if self.direction == 'up':
            self.y[0] -= BLOCK_SIZE
        elif self.direction == 'down':
            self.y[0] += BLOCK_SIZE
        elif self.direction == 'left':
            self.x[0] -= BLOCK_SIZE
        elif self.direction == 'right':
            self.x[0] += BLOCK_SIZE

    def increase(self):
        self.length += 1
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        self.surface.fill(BACKGROUND_COLOR)
        self.snake = Snake(self.surface, 1)
        self.snake.draw()
        self.apple = Apple(self.surface)
        self.apple.draw()
        self.delay = 0.5
        self.paused = False

    def is_collision(self, x0, y0, x, y):
        if (x0 <= x < x0 + BLOCK_SIZE) and (
                y0 <= y < y0 + BLOCK_SIZE):
            return True

    def play(self):
        # move snake:
        self.snake.walk()

        # check if snake collides with itself:
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0],
                                 self.snake.x[i], self.snake.y[i]):
                raise GameOver

        # check if snake is out of screen:
        if self.snake.x[0] < 0 or \
                self.snake.x[0] >= WINDOW_SIZE[0] or \
                self.snake.y[0] < 0 or \
                self.snake.y[0] >= WINDOW_SIZE[1]:
            raise GameOver

        # check if snake collides with apple:
        if self.is_collision(self.apple.x, self.apple.y,
                             self.snake.x[0], self.snake.y[0]):

            if self.snake.length >= HORIZONTAL_SPACES * VERTICAL_SPACES:
                raise GameOver

            self.snake.increase()

            # check if apple is in same place as snake:
            apple_in_snake = True
            count = 0
            while apple_in_snake:

                self.apple.move()
                apple_in_snake = False

                count += 1

                for i in range(self.snake.length):
                    if self.is_collision(self.apple.x, self.apple.y,
                                         self.snake.x[i], self.snake.y[i]):
                        apple_in_snake = True

            # increases difficulty by making it faster:
            if self.snake.length > 10:
                self.delay = 0.2

    def draw(self):
        self.surface.fill(BACKGROUND_COLOR)
        self.display_score()
        self.snake.draw()
        self.apple.draw()
        pygame.display.flip()

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

    def reset(self):
        self.snake = Snake(self.surface, 1)
        self.apple = Apple(self.surface)

    def run(self):
        running = True

        # Event Loop:
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:

                    # Exit key
                    if event.key == K_ESCAPE:
                        running = False

                    # Pause / Unpause:
                    elif event.key == K_RETURN:
                        self.paused = not self.paused

                    if not self.paused:

                        # Snake movement:
                        if event.key == K_UP:
                            self.snake.move_up()

                        elif event.key == K_DOWN:
                            self.snake.move_down()

                        elif event.key == K_LEFT:
                            self.snake.move_left()

                        elif event.key == K_RIGHT:
                            self.snake.move_right()

                elif event.type == QUIT:
                    running = False

            try:
                if not self.paused:
                    self.play()
                    self.draw()

            except GameOver:
                self.paused = True
                self.display_game_over()
                self.reset()

            time.sleep(self.delay)


if __name__ == "__main__":
    print("Starting game!")
    game = Game()
    game.run()
    print("Game closed!")
