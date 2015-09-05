# -*- coding: utf-8 -*-
import pygame
from pygame import Color

def draw_messageboard(screen, rect, messages, font_size = 20, color = Color('black')):
    my_font = pygame.font.SysFont('arial', font_size)
    msgs_r = [my_font.render(msg, True, color)
              for msg in messages]
    height = msgs_r[0].get_height()
    for i in range(len(msgs_r)):
        screen.blit(msgs_r[i], rect.move(0, i * height))

class ProgressBar(object):

    def __init__(self, screen):
        self.screen = screen
        self.filled = 0
        self.corner = (0, 0)

    def set_filled(self, x):
        self.filled = x

    def set_corner(self, c):
        self.corner = c

    def draw(self):
        pygame.draw.rect(self.screen, Color('black'),
            pygame.Rect(self.corner[0], self.corner[1], 52, 9), 2)
        tofill = self.filled // 2
        self.screen.fill(Color('red'),
            (self.corner[0] + 2, self.corner[1] + 2, tofill, 6))


