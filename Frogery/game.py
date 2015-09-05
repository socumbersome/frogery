# -*- coding: utf-8 -*-
import sys
import datetime
import pygame
from pygame.locals import *
from pygame import Color
import pygame.gfxdraw
from hydrophyte import Hydrophyte
from fly import Fly
from frog import Frog
import random
from utils import *
from widgets import *
from timemachine import *

class Game(object):
    ONGOING, ENDED, REWINDING = range(3)
    EASY, NORMAL, HARD, HELL = range(4)
    def __init__(self, screen, difficulty, onexit):
        self.screen = screen
        self.onexit = onexit
        self.dtime = 0
        self.number_of_hydrophytes = 8
        self.number_of_flies = 30
        self.hydrophytes = []
        self.create_hydrophytes()
        self.flies = []
        self.create_flies()
        self.difficulty = self._get_difficulty(difficulty)
        self.frog = self.create_frog(False)
        self.frog_ai = None
        self.jump_assistant = False
        self.assistant_target = (0, 0)
        if self.difficulty in [Game.EASY, Game.HARD]:
            self.jump_assistant = True
        if self.difficulty in [Game.HARD, Game.HELL]:
            self.frog_ai = self.create_frog(True)
        self.bg_color = Color(50, 210, 230)
        self.state = Game.ONGOING
        self.MESSAGE_RECT = Rect(5, 5, 120, 100)
        self.game_time = '00:00'
        self.START_TIME = datetime.datetime.now()
        self.CURR_TIME = datetime.datetime.now()
        self.jump_strength = 0
        self.accumulating_strength = False
        self.frogs_bar = ProgressBar(self.screen)
        self.timemach = TimeMachine(310)
        timestamp = self.get_timestamp()
        self.timemach.set_genesis(timestamp)
        pygame.mouse.set_visible(True)

    def _get_difficulty(self, s):
        sl = s.lower()
        if sl == "easy":
            return Game.EASY
        if sl == "normal":
            return Game.NORMAL
        if sl == "hard":
            return Game.HARD
        return Game.HELL

    def create_hydrophytes(self):
        ratiow = self.screen.get_width() // (self.number_of_hydrophytes - 2)
        ratioh = self.screen.get_height() // (self.number_of_hydrophytes - 2)
        for n in range(self.number_of_hydrophytes - 2):
            size = random.randint(30, 45)
            x = n * ratiow + size
            y = n * ratioh + size
            vx = random.randint(10, 35)
            vy = random.randint(10, 35)
            dx, dy = random.choice([-1, 1]), random.choice([-1, 1])
            vx *= dx
            vy *= dy
            hp = Hydrophyte(self.screen, point2vec(x, y), size,
                            point2vec(vx, vy))
            self.hydrophytes.append(hp)

        size = random.randint(45, 60)
        x = ratiow + size
        y = (self.number_of_hydrophytes - 3) * ratioh + size
        vx = random.randint(-25, 25)
        vy = random.randint(-25, 25)
        hp = Hydrophyte(self.screen, point2vec(x, y), size,
                            point2vec(vx, vy))
        self.hydrophytes.append(hp)
        hp = Hydrophyte(self.screen, point2vec(y, x), size,
                            point2vec(vx, vy))
        self.hydrophytes.append(hp)

    def create_flies(self):
        for n in range(self.number_of_flies):
            x = random.randint(1, self.screen.get_width() - 1)
            y = random.randint(1, self.screen.get_height() - 1)
            vx = random.randint(30, 150)
            vy = random.randint(30, 150)
            delay = random.randint(1, 6)
            fl = Fly(self.screen, point2vec(x, y),
                     point2vec(vx, vy), delay)
            self.flies.append(fl)

    def create_frog(self, ai):
        hp = random.choice(self.hydrophytes)
        if ai:
            while hp == self.frog.anchor:
                hp = random.choice(self.hydrophytes)
        f = Frog(self.screen, hp, self.hydrophytes,
                 self.flies, ai)
        return f

    def set_dtime(self, dtime):
        self.dtime = dtime

    def _target_hydrophyte(self):
        landing = self.frog.get_position_v()
        vel, time = self.frog.get_jumping_param(self.jump_strength)
        landing += vel * time
        landp = vec2point(landing)
        self.assistant_target = landp
        for hp in self.hydrophytes:
            hp.unmark()
            if hp.point_is_inside(landp):
                hp.mark()

    def get_timestamp(self):
        return TimeStamp(self.frog, self.frog_ai,
            self.hydrophytes, self.flies)

    def remaining_flies(self):
        ans = 0
        for fl in self.flies:
            if fl.alive:
                ans += 1
        return ans

    def toggle_state(self):
        if self.state == Game.ENDED:
            # resurrect
            self.state = Game.REWINDING
            return
        elif self.state == Game.ONGOING:
            self.state = Game.REWINDING
            return
        elif self.state == Game.REWINDING:
            self.timemach.stop_travelling() # crucial! otherwise we would
            # be able to travel back indefinitely
            self.accumulating_strength = False
            self.state = Game.ONGOING

    def handleEvents(self):
        if self.state == Game.REWINDING:
            ts = self.timemach.get_previous_timestamp()
            if ts is not None:
                ts.make_it_reality(self.frog, self.frog_ai,
                    self.hydrophytes, self.flies, self.frogs_bar)
            else:
                self.toggle_state()
        if self.state == Game.ONGOING:
            self.timemach.add_timestamp(self.get_timestamp())

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self.onexit
                elif event.key == pygame.K_r:
                    self.toggle_state()
            if self.state == Game.ONGOING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.frog.eat()
                    elif event.key == pygame.K_SPACE:
                        self.accumulating_strength = True
                        self.jump_strength = 0
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.frog.jump(self.jump_strength)
                        self.accumulating_strength = False

        if self.state in [Game.ENDED, Game.REWINDING]:
            return

        fp = self.frog.get_position_p()
        self.frogs_bar.set_corner((fp[0] - 25, fp[1] - 40))

        if self.accumulating_strength:
            self.jump_strength = (self.jump_strength + 1.5) % 101
            self.frogs_bar.set_filled(self.jump_strength)
            if self.jump_assistant:
                self._target_hydrophyte()
        else:
            self.jump_strength = 0
            self.frogs_bar.set_filled(self.jump_strength)

        for index, hp in enumerate(self.hydrophytes):
            hp.move(self.dtime)
            for hp2 in self.hydrophytes[index + 1:]:
                hp.collide(hp2, self.dtime)

        for fl in self.flies:
            if fl.alive:
                fl.move(self.dtime)

        if self.remaining_flies() == 0 or self.frog.state == Frog.DROWNING:
            self.state = Game.ENDED
            return

        self.frog.move(self.dtime)
        if self.frog_ai is not None:
            self.frog_ai.ai_make_decision()
            self.frog_ai.move(self.dtime)

    def draw(self):
        self.screen.fill(self.bg_color)
        for hp in self.hydrophytes:
            hp.draw()
        self.frog.draw()
        if self.frog_ai is not None:
            self.frog_ai.draw()
        for fl in self.flies:
            if fl.alive:
                fl.draw()

        #comment this out not to see ai's target !
        #if self.frog_ai is not None:
        #    self.frog_ai.draw_target()

        self.frogs_bar.draw()
        if self.jump_assistant and self.accumulating_strength:
            pygame.draw.circle(self.screen, Color('red'),
                               self.assistant_target, 3)

        msg1 = 'Flies: %d' % self.remaining_flies()
        msg2 = 'You ate: %d' % self.frog.eaten_flies
        msg3 = ''
        if self.frog_ai is not None:
            msg3 = 'Opponent ate: %d' % self.frog_ai.eaten_flies
        msg4 = ''
        if self.state == Game.ENDED:
            if self.frog_ai is not None:
                if self.remaining_flies() == 0:
                    if self.frog.eaten_flies > self.frog_ai.eaten_flies:
                        msg4 = "You've beaten him!"
                        if self.frog.is_drowned():
                            msg4 += " although you're dead xD"
                    elif self.frog.eaten_flies < self.frog_ai.eaten_flies:
                        msg4 = "He's beaten you..."
                        if self.frog_ai.is_drowned():
                            msg4 += " although he's dead xD"
                    else:
                        msg4 = "Ended in a tie!"
                else:
                    msg4 = 'You drowned...'
            else:
                if self.remaining_flies() == 0:
                    msg4 = 'You won!'
                else:
                    msg4 = 'You drowned...'
        if self.state != Game.ENDED:
            self.CURR_TIME = datetime.datetime.now()
            duration = self.CURR_TIME - self.START_TIME
            secs = duration.total_seconds()
            secs = int(secs)
            minutes = int(secs / 60) % 60
            secs = secs % 60
            self.game_time = str(minutes).zfill(2) + ":" + str(secs).zfill(2)
        msgslist = [msg1, self.game_time, msg2]
        if self.frog_ai is not None:
            msgslist.append(msg3)
        if self.state == Game.ENDED:
            msgslist.append(msg4)
            msgslist.append('Press ESC to go to menu')
        draw_messageboard(self.screen, self.MESSAGE_RECT, msgslist)

        if self.state == Game.REWINDING:
            draw_messageboard(self.screen, Rect(200, 5, 120, 100), "R",
                 font_size = 60, color = Color('red'))

