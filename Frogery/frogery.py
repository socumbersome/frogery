# -*- coding: utf-8 -*-
import sys

import pygame
from pygame.locals import *

from menu.gamemenu import GameMenu
from game import Game
from instructions import Instructions

class Frogery(object):
    SCREEN_DIMENSIONS = SCREEN_WIDTH, SCREEN_HEIGHT = 500, 500
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_DIMENSIONS)
        pygame.display.set_caption('Frogery')
        menuEntries = self._createMenuEntries()
        self.menu = GameMenu(self.screen, menuEntries)
        self.game = None
        self.instr = Instructions(self.screen, self.goToMenu)
        self.clock = pygame.time.Clock()
        self.active_part = self.menu

    def _createMenuEntries(self):
        entries = [("Easy mode", self.startGameEasy),
                   ("Normal mode", self.startGameNormal),
                   ("Hard mode", self.startGameHard),
                   ("Hell (of a) mode", self.startGameHell),
                   ("Instructions", self.instructions),
                   ("Quit game", self.quit)]
        return entries

    def startGameEasy(self):
        self.game = Game(self.screen, "easy", self.goToMenu)
        self.active_part = self.game

    def startGameNormal(self):
        self.game = Game(self.screen, "normal", self.goToMenu)
        self.active_part = self.game

    def startGameHard(self):
        self.game = Game(self.screen, "hard", self.goToMenu)
        self.active_part = self.game

    def startGameHell(self):
        self.game = Game(self.screen, "hell", self.goToMenu)
        self.active_part = self.game

    def instructions(self):
        self.active_part = self.instr

    def goToMenu(self):
        self.active_part = self.menu

    def run(self):
        while True:
            time_passed = self.clock.tick(60)
            dtime = time_passed / 1000.0
            if self.game is not None:
                self.game.set_dtime(dtime)

            # If too long has passed between two frames, don't
            # update (the game must have been suspended for some
            # reason, and we don't want it to "jump forward" suddenly)
            if time_passed > 100:
                continue

            callback = None
            if self.active_part:
                callback = self.active_part.handleEvents()
                if not callback:
                    self.active_part.draw()
                else:
                    callback()

            pygame.display.flip()

    def quit(self):
        sys.exit()


if __name__ == '__main__':
    frogery = Frogery()
    frogery.run()