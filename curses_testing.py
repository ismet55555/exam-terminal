#!/usr/bin/env python

import curses 

screen = curses.initscr()

try:
    screen.border(0)

    box1 = curses.newwin(20, 20, 5, 5)
    box1.box()    

    screen.refresh()
    box1.refresh()

    screen.getch()

finally:
    curses.endwin()