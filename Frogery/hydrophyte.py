# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from pygame.sprite import Sprite
from utils import *
from actor import Actor

class Hydrophyte(Actor):
    UNMARKED, MARKED = range(2)
    imgs = ['images/plant.png', 'images/plant_marked.png']
    def __init__(self, screen, position, size, velocity):
        Actor.__init__(self, screen, position, size, velocity)
        self.friction = 0.3
        self.state = Hydrophyte.UNMARKED
        self.images = [pygame.image.load(ur).convert() for ur in Hydrophyte.imgs]
        for im in self.images:
            im.set_colorkey((0,0,0))
        self.images[0] = pygame.transform.scale(self.images[0], (2*size, 2*size))
        self.images[1] = pygame.transform.scale(self.images[1], (2*size, 2*size))
        self.image_w, self.image_h = self.images[0].get_size()
        self.phase_threshold_time = 0.5
        self.sema_drown = 2 # semaphor - when equal to 0, then hydrophyte's drowning
        self.phase_time = 0

    def mark(self):
        self.state = Hydrophyte.MARKED

    def unmark(self):
        self.state = Hydrophyte.UNMARKED

    def draw(self):
        image = self.images[self.state]
        draw_rect = image.get_rect().move(
            self.position.x - self.image_w // 2,
            self.position.y - self.image_h // 2)
        self.screen.blit(image, draw_rect)

    def point_is_inside(self, point):
        v = point2vec(point) - self.get_position_v()
        return v.magnitude() < self.size

    def drowned(self):
        return (self.images[0].get_alpha() <= 20)

    def nearly_drowned(self):
        return (self.images[0].get_alpha() <= 60)

    def change_alpha(self, x):
        for im in self.images:
            if x > 0:
                im.set_alpha(min(255, im.get_alpha() + x))
            elif x < 0:
                im.set_alpha(max(0, im.get_alpha() + x))

    def jumped_on(self):
        self.sema_drown -= 1

    def jumped_off(self):
        self.sema_drown += 1

    def move(self, dtime):
        if self.sema_drown < 2:
            self.phase_time += dtime
            if self.phase_time >= self.phase_threshold_time:
                self.change_alpha(-20)
                self.phase_time = 0
            else:
                pass
        else:
            self.phase_time += dtime
            if self.phase_time >= self.phase_threshold_time:
                self.change_alpha(20)
                self.phase_time = 0

        self.position += self.velocity * dtime
        if self.velocity.magnitude() > dtime * self.friction:
            velocity_direction = self.velocity.normalized()
            friction_direction = -velocity_direction
            self.velocity += friction_direction * dtime

        self.bounce()

    def distance(self, other, dtime):
        radiiAB = self.size + other.size
        posA = self.position + self.velocity * dtime
        posB = other.position + other.velocity * dtime
        posAB = abs(posA - posB)
        return posAB - radiiAB

    def collide(self, other, dtime):
        if self.distance(other, dtime) <= 0:
            collision_vec = self.position - other.position
            collision_vec.normalize()
            self.velocity = self.velocity.reflect(collision_vec)
            other.velocity = other.velocity.reflect(collision_vec)

    def get_state(self):
        return [self.position.copy(), self.velocity.copy(),
                self.images[0].get_alpha(), self.sema_drown, self.phase_time]

    def set_state(self, hpstate):
        self.position = hpstate[0]
        self.velocity = hpstate[1]
        for im in self.images:
            im.set_alpha(hpstate[2])
        self.sema_drown = hpstate[3]
        self.phase_time = hpstate[4]
        self.state = Hydrophyte.UNMARKED