# -*- coding: utf-8 -*-
import sys
import pygame
from pygame.locals import *
from pygame import Color
from widgets import draw_messageboard

class Instructions(object):

    def __init__(self, screen, onexit):
        self.screen = screen
        self.onexit = onexit
        self.messages = ['Try to eat all flies as fastest as you can!',
            'And beware of water! Mr Frog cannot swim...',
            ' ',
            'Game comes with 4 difficulty modes: easy, normal, hard and hell.',
            'Modes easy and normal are without an opponent frog, as oppossed',
            'to hard and hell. Additionally, modes easy and hard provides',
            'have turned on a built-in jump assistant, which can be invaluable',
            'to precisely target a hydrophyte.',
            '',
            'Controls:',
            'By moving the cursor of your mouse you can rotate Mr Frog.',
            'Pressing "F" key will cause Mr Frog to try to snap all flies within',
             'the reach of his tongue.',
            'By keeping pressed a spacebar, you can set the strength of a jump',
             '- just release it when a strength-bar is showing appropriate strength.',
             'By pressing "R" key you can toggle time travel up to five seconds long',
             '- however, if you go back in time to a certain point not using',
             'all available time span, you will set a time barrier that will',
             'never allow you to go back even further, even if it would take',
             'less than 5 seconds - so use it judiciously!',
             'Mind you - you can even resurrect this way...'
            '',
            'Pressing ESC key makes you return to the menu.',
            '',
            'Author: Patryk Kajdas',
            ''
            ]

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and \
                event.key == pygame.K_ESCAPE:
                return self.onexit

    def draw(self):
        self.screen.fill(Color(200, 180, 200))
        draw_messageboard(self.screen, self.screen.get_rect(), self.messages, 16)
