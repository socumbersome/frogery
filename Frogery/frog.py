# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from pygame.sprite import Sprite
import math, random
from utils import *

class Frog(Sprite):
    SITTING, JUMPING, EATING, DROWNING = range(4)
    imgs = ['images/frog_sitting.png',
            'images/frog_jumping.png',
            'images/frog_eating.png']
    imgs_ai = ['images/frog2_sitting.png',
               'images/frog2_jumping.png',
               'images/frog2_eating.png']
    def __init__(self, screen, anchor, hydrophytes, flies, ai):
        Sprite.__init__(self)
        self.screen = screen
        self.anchor = anchor
        self.anchor.jumped_on()
        self.hydrophytes = hydrophytes
        self.flies = flies
        self.ai = ai
        imm = Frog.imgs_ai if ai else Frog.imgs
        self.ai_prey = random.choice(self.flies)
        self.ai_tanchor = anchor
        self.ai_target = self.ai_prey
        self.images = [pygame.image.load(ur).convert_alpha() for ur in imm]
        self.image = self.images[0]
        self.image_w, self.image_h = self.image.get_size()
        self.angle = 0
        self.velocity = point2vec(0, 0)
        self.base_position = anchor.get_position_v()
        self.rel_position = point2vec(0, 0)
        self.state = Frog.SITTING
        self.jumping_time = 0
        self.already_jumping_time = 0
        self.already_eating = 0
        self.eating_time = 0.25
        self.eaten_flies = 0
        self.ai_resting_time = 1
        self.ai_already_resting_time = 0

    def draw(self):
        if self.state == Frog.SITTING:
            self.image = self.images[0]
        elif self.state == Frog.JUMPING:
            self.image = self.images[1]
        elif self.state == Frog.EATING:
            self.image = self.images[2]
        else:
            return
        imm = pygame.transform.rotate(self.image, self.angle)
        imw, imh = imm.get_size()
        rx, ry = self.get_position_p()
        draw_rect = imm.get_rect().move(
            rx - imw // 2,
            ry - imh // 2)
        self.screen.blit(imm, draw_rect)

    def remaining_flies(self):
        ans = 0
        for fl in self.flies:
            if fl.alive:
                ans += 1
        return ans

    def draw_target(self):
        pygame.draw.circle(self.screen, Color('orange'),
                           self.ai_target.get_position_p(), 5)

    def is_drowned(self):
       return self.state == Frog.DROWNING

    def point_is_caught(self, point):
        if self.ai:
            m  = self.ai_target.get_position_v()
        else:
            m = point2vec(pygame.mouse.get_pos())
        f = self.get_position_v()
        direct = m - f
        direct.normalize()
        direct *= 60  # heuristic
        pt = point2vec(point)
        topoint = pt - f
        angle = direct.normalized().angle(topoint.normalized())
        angle = math.degrees(angle)
        if (angle < 10 and angle > -10 and
            topoint.magnitude() < direct.magnitude()):
            return True
        return False

    def get_position_p(self):
        return vec2point(self.get_position_v())

    def get_position_v(self):
        return self.base_position + self.rel_position

    def move(self, dtime):
        if self.anchor is not None:
            if self.anchor.drowned():
                self.state = Frog.DROWNING

        if self.ai:
            mx, my = self.ai_target.get_position_p()
        else:
            mx, my = pygame.mouse.get_pos()
        fx, fy = self.get_position_p()
        self.angle = math.degrees(math.atan2(fx - mx, fy - my))

        if self.state == Frog.JUMPING:
            self.already_jumping_time += dtime
            if(self.already_jumping_time >= self.jumping_time):
                self._settle()
            else:
                self.base_position += self.velocity * dtime
        elif ((self.state == Frog.SITTING or self.state == Frog.EATING)
              and self.anchor):
            self.base_position = self.anchor.get_position_v()
            if self.ai:
                if self.ai_already_resting_time < self.ai_resting_time:
                    self.ai_already_resting_time += dtime

            if self.state == Frog.EATING:
                self.already_eating += dtime
                if self.already_eating >= self.eating_time:
                    self.state = Frog.SITTING
                    self.already_eating = 0
                    self.ai_already_resting_time = 0
                else:
                    for fly in self.flies:
                        if not fly.alive:
                            continue
                        if self.point_is_caught(fly.get_position_p()):
                            fly.kill()
                            self.eaten_flies += 1

    def _settle(self):
        curr_pos = self.get_position_v()
        curr_pos_p = vec2point(curr_pos)
        for hp in self.hydrophytes:
            if hp.point_is_inside(curr_pos_p):
                self.state = Frog.SITTING
                self.anchor = hp
                hp.jumped_on()
                anchor = hp.get_position_v()
                self.base_position = anchor
                self.rel_position = curr_pos - anchor
                self.anchor.velocity += self.velocity / 7.0
                if self.ai:
                    self._ai_target_prey()
                    self.ai_target = self.ai_prey
                return
        self.state = Frog.DROWNING

    def _ai_target_prey(self): # return True iff targeted successfully
        if self.remaining_flies() == 0:
            return False
        closest = None
        closest_dist = 0
        fr = self.get_position_v()
        for fly in self.flies:
            if not fly.alive:
                continue
            fl = fly.get_position_v()
            e = fl - fr
            if closest is None or e.magnitude() < closest_dist:
                closest = fly
                closest_dist = e.magnitude()
        self.ai_prey = closest
        return True

    def _ai_target_anchor(self):
        if self.anchor is None:
            return False
        curr = self.anchor
        new = None
        fp = self.get_position_v()
        while True:
            new = random.choice(self.hydrophytes)
            hp = new.get_position_v()
            e = hp - fp
            if new != curr and e.magnitude() < 350:
                self.tanchor = new
                return True

    def ai_make_decision(self):
        if self.anchor is not None and self.anchor.nearly_drowned():
            self._ai_target_anchor()
            self.ai_target = self.tanchor
            m = self.tanchor.get_position_v()
            f = self.get_position_v()
            aux = f - m
            # magic below - see get_jumping_param() to understand why that way
            strength = (30*30 * aux.magnitude_squared()) ** (1 / 3.0)
            strength /= 5.0
            self.jump(strength)
        elif self.state == Frog.SITTING:
            self._ai_hunt()

    def _ai_hunt(self):
        self._ai_target_prey()
        self.ai_target = self.ai_prey
        if self.ai_already_resting_time < self.ai_resting_time:
            return
        fl = self.ai_prey.get_position_v()
        e = fl - self.get_position_v()
        if e.magnitude() < 40:
            self.eat()


    def get_jumping_param(self, strength):
        # return tuple (v, t) ; v - velocity vector, t - jumping time
        m = None
        if self.ai:
            m = self.ai_target.get_position_v()
        else:
            m = point2vec(pygame.mouse.get_pos())
        f = self.get_position_v()
        vel = m - f
        vel.normalize()
        vel *= 5 * strength
        jt = math.sqrt(vel.magnitude()) / 30.0
        return (vel, jt)

    def jump(self, strength):
        if self.state == Frog.JUMPING:
            return
        self.base_position = self.get_position_v()
        self.rel_position = point2vec(0, 0)
        self.velocity, self.jumping_time = self.get_jumping_param(strength)
        self.already_jumping_time = 0
        if self.anchor:
            self.anchor.velocity -= self.velocity / 12.0
            self.anchor.jumped_off()
        self.state = Frog.JUMPING
        self.anchor = None

    def eat(self):
        if self.state != Frog.SITTING:
            return
        self.state = Frog.EATING

    def get_state(self):
        return [self.base_position.copy(), self.rel_position.copy(),
            self.velocity.copy(), self.state, self.anchor, self.angle,
            self.eaten_flies, self.jumping_time, self.already_jumping_time,
            self.already_eating]

    def ai_get_state(self):
        return self.get_state() + [self.ai_prey, self.ai_tanchor,
            self.ai_target]

    def set_state(self, frogstate):
        self.base_position = frogstate[0]
        self.rel_position = frogstate[1]
        self.velocity = frogstate[2]
        self.state = frogstate[3]
        self.anchor = frogstate[4]
        self.angle = frogstate[5]
        self.eaten_flies = frogstate[6]
        self.jumping_time = frogstate[7]
        self.already_jumping_time = frogstate[8]
        self.already_eating = frogstate[9]

    def ai_set_state(self, aifrogstate):
        self.set_state(aifrogstate)
        self.ai_prey = aifrogstate[10]
        self.ai_tanchor = aifrogstate[11]
        self.ai_target = aifrogstate[12]