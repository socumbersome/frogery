# -*- coding: utf-8 -*-

from pygame.locals import *
from pygame.sprite import Sprite
from utils import *

class Actor(Sprite):

    def __init__(self, screen, position, size, velocity):
        Sprite.__init__(self)
        self.screen = screen
        self.position = position
        self.size = size
        self.velocity = velocity

    def bounce(self):
        if self.position.x <= self.size:
            self.position.x = 2*self.size - self.position.x
            self.velocity = self.velocity.reflect(point2vec(1,0))
        elif self.position.x >= self.screen.get_width() - self.size:
            self.position.x = 2*(self.screen.get_width() - self.size) - self.position.x
            self.velocity = self.velocity.reflect(point2vec(1,0))

        if self.position.y <= self.size:
            self.position.y = 2*self.size - self.position.y
            self.velocity = self.velocity.reflect(point2vec(0,1))
        elif self.position.y >= self.screen.get_height() - self.size:
            self.position.y = 2*(self.screen.get_height() - self.size) - self.position.y
            self.velocity = self.velocity.reflect(point2vec(0,1))

    def get_position_p(self):
        return vec2point(self.get_position_v())

    def get_position_v(self):
        return self.position

