# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from pygame import Color
import sys

class MenuItem(pygame.font.Font):

    def __init__(self, text, font = None, font_size = 32,
                 active_font_color = Color("White"),
                 inactive_font_color = Color("Black"),
                 position = (0, 0), callback = None):
        pygame.font.Font.__init__(self, font, font_size)
        self.text = text
        self.font_size = font_size
        self.active_font_color = active_font_color
        self.inactive_font_color = inactive_font_color
        self.label = self.render(self.text, 1, self.inactive_font_color)
        self.width = self.label.get_rect().width
        self.height = self.label.get_rect().height
        self.position = position
        self.callback = callback

    def set_position(self, newpos):
        self.position = newpos

    def make_active(self):
        self.label = self.render(self.text, 1, self.active_font_color)

    def make_inactive(self):
        self.label = self.render(self.text, 1, self.inactive_font_color)

    def is_mouse_selection(self, position):
        posx, posy = position
        selfposx, selfposy = self.position
        return (posx >= selfposx and posx <= selfposx + self.width and \
            posy >= selfposy and posy <= selfposy + self.height)


class GameMenu(object):

    def __init__(self, screen, menuEntriesLogic):
        ''' menuEntriesLogic is a list [(text_entry, callback)]+ '''
        self.screen = screen
        self.SCREEN_WIDTH = self.screen.get_rect().width
        self.SCREEN_HEIGHT = self.screen.get_rect().height
        self.cur_item = 0
        self.bg_color = Color(50, 150, 50)
        self.mouse_is_visible = True
        self.entryToCallback = {t[0]:t[1] for t in menuEntriesLogic}
        self.menuItems = []
        for index, (text, _) in enumerate(menuEntriesLogic):
            menu_item = MenuItem(text, callback = self.entryToCallback[text])

            total_height = len(menuEntriesLogic) * menu_item.height
            pos_x = (self.SCREEN_WIDTH // 2) - (menu_item.width // 2)
            pos_y = (self.SCREEN_HEIGHT // 2) - (total_height // 2) + \
                   (index * (menu_item.height + 2))
            menu_item.set_position((pos_x, pos_y))
            self.menuItems.append(menu_item)

    def draw(self):
        self.screen.fill(self.bg_color)
        for item in self.menuItems:
            self.screen.blit(item.label, item.position)

    def set_mouse_visibility(self):
        if self.mouse_is_visible:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

    def set_mouse_selection(self, index, mouse_pos):
        item = self.menuItems[index]
        if item.is_mouse_selection(mouse_pos):
            item.make_active()
            self.cur_item = index
        else:
            item.make_inactive()

    def set_keyb_selection(self, key):
        for item in self.menuItems:
            item.make_inactive()

        if key == pygame.K_UP and self.cur_item > 0:
            self.cur_item -= 1
        elif key == pygame.K_DOWN and \
            self.cur_item < len(self.menuItems) - 1:
            self.cur_item += 1

        self.menuItems[self.cur_item].make_active()

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.mouse_is_visible = False
                self.set_keyb_selection(event.key)
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    text = self.menuItems[self.cur_item].text
                    return self.entryToCallback[text]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mpos = pygame.mouse.get_pos()
                for item in self.menuItems:
                    if item.is_mouse_selection(mpos):
                        return self.entryToCallback[item.text]

        if pygame.mouse.get_rel() != (0, 0):
            self.mouse_is_visible = True
        self.set_mouse_visibility()

        if self.mouse_is_visible:
            for index in range(len(self.menuItems)):
                mpos = pygame.mouse.get_pos()
                self.set_mouse_selection(index, mpos)


