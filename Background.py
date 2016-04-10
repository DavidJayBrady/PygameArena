import pygame
from Mover import Mover

class Background(Mover):
    def __init__(self):
        Mover.__init__(self)
        self.image = pygame.image.load('Walls_Background/Background.png')
        self.rect = self.image.get_rect() # pygame.Rect

class Wall(Mover):
    def __init__(self, image, x, y):
        Mover.__init__(self)
        self.image = pygame.image.load('Walls_Background/' + image + '.png')
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


    def handle_collision(self, _):
        pass

    def is_dead(self):
        pass

    @staticmethod
    def gather_walls():
        # Wall One: Center Vertical
        # Wall Two: Center Horizontal
        # Walls 3-6: Middles sticking in towards center.
        # Walls 7/9: Top/Bot
        # Walls 8/10: Left/Right

        x_cords = [1808, 976, 3136, 1808, 64, 1808, 64, 3776, 0, 0]
        y_cords = [608, 976, 960, 16, 976, 1776, 2176, 0, 0, 0]
        walls = pygame.sprite.Group()
        for i in range(1, 11):
            walls.add(Wall(str(i), x_cords[i-1], y_cords[i-1]))
        return walls


