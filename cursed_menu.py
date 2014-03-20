#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import unicode_literals

import curses
import yaml
import os.path
import subprocess
import locale


def load_config():
    config_raw = open(os.path.join(os.path.dirname(__file__), 'config.yaml')).read()
    config_dict = yaml.load(config_raw)
    return config_dict


class MainWindow(object):
    def __init__(self, config):
        self.window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)  # invisible cursor
        self.window.keypad(1)
        self.__config = config
        self.background = Picture(size_x=self.__config['main']['size_x'],
                                  size_y=self.__config['main']['size_y'],
                                  pic_file=self.__config['main']['picture'])
        self.background.draw(self.window)
        self.elements = []
        self.__init_elements()
        self.selected = -1  # index of selected element

    def __init_elements(self):
        for i in range(len(self.__config['elements'])):
            self.elements.append(Element(
                size_x=self.__config['main']['element_size_x'],
                size_y=self.__config['main']['element_size_y'],
                offset_x=self.__config['main']['element_offset_x'],
                offset_y=self.__config['main']['element_offset_y'] +
                         i * (self.__config['main']['element_size_y'] +
                              self.__config['main']['element_interval']),
                picture=self.__config['elements'][i]['picture'],
                action=self.__config['elements'][i]['action']
            ))

    def run(self):
        try:
            while True:
                key = self.window.getch()
                if key == curses.KEY_UP:
                    self.__select_prev()
                elif key == curses.KEY_DOWN:
                    self.__select_next()
                elif key == curses.KEY_ENTER or key == 10:
                    self.elements[self.selected].activate()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise e
        finally:
            self.window.keypad(0)
            curses.nocbreak()
            curses.echo()
            curses.endwin()

    def __select_next(self):
        if len(self.elements) > self.selected + 1:
            self.elements[self.selected].unfocus()
            self.selected += 1
            self.elements[self.selected].focus()

    def __select_prev(self):
        if self.selected > 0:
            self.elements[self.selected].unfocus()
            self.selected -= 1
            self.elements[self.selected].focus()
        elif self.selected == -1:
            self.selected = 0
            self.elements[0].focus()


class Element(object):
    def __init__(self, size_x, size_y, offset_x, offset_y, picture, action):
        self.__window = curses.newwin(size_y, size_x, offset_y, offset_x)
        self.__picture = Picture(size_x, size_y, picture)
        self.__action = action

        self.__picture.draw(self.__window)

    def focus(self):
        self.__window.box()
        self.__window.refresh()

    def unfocus(self):
        self.__window.border(1, 1, 1, 1, 1, 1, 1, 1)  # 1 is the blank char code
        self.__picture.draw(self.__window)
        self.__window.refresh()

    def activate(self):
        subprocess.Popen(self.__action,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        exit(0)


class Picture(object):
    def __init__(self, size_x, size_y, pic_file):
        raw_pic = open(os.path.join(os.path.dirname(__file__), 'pictures', pic_file)).read().decode('utf-8')
        self.__lines = raw_pic.splitlines()[:size_y]
        self.__lines = map(lambda x: x.ljust(size_x - 1), self.__lines)
        self.__lines = map(lambda x: x[:size_x], self.__lines)

    def draw(self, window):
        for i in xrange(len(self.__lines)):
            window.addstr(i, 0, self.__lines[i].encode('utf-8'))
        window.refresh()


config = load_config()

locale.setlocale(locale.LC_ALL, '')

a = MainWindow(config)
a.run()