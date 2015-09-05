# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import random
import math
from utils import *
from actor import Actor

class Fly(Actor):

    def __init__(self, screen, position, velocity, delay = 1):
        Actor.__init__(self, screen, position, 10, velocity)
        self.image = pygame.image.load('images/fly.png').convert_alpha()
        self.image_w, self.image_h = self.image.get_size()
        self.delay = delay
        self.acc_time = 0
        self.alive = True

    def draw(self):
        draw_rect = self.image.get_rect().move(
            self.position.x - self.image_w // 2,
            self.position.y - self.image_h // 2)
        self.screen.blit(self.image, draw_rect)

    def move(self, dtime):
        self.position += self.velocity * dtime
        self.acc_time += dtime
        if self.acc_time > self.delay:
            self._set_random_direction()
            self.acc_time = 0
        self.bounce()

    def kill(self):
        self.alive = False

    def _set_random_direction(self):
        new_angle = random.uniform(0, math.pi*2)
        new_x = math.sin(new_angle)
        new_y = math.cos(new_angle)
        new_vector = point2vec(new_x, new_y)
        new_vector.normalize()
        new_vector *= self.velocity.magnitude()
        self.velocity = new_vector

    def get_state(self):
        return [self.position.copy(), self.velocity.copy(), self.alive]

    def set_state(self, flystate):
        self.position = flystate[0]
        self.velocity = flystate[1]
        self.alive = flystate[2]