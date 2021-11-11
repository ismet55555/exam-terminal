#!/usr/bin/env python3

import curses

stdscr = curses.initscr()

# Turn off echo
curses.noecho()

# Non-blocking for user
stdscr.nodelay(True)

# Start colors in curses and initiate a color
curses.start_color()
curses.init_pair(1, 235, curses.COLOR_WHITE)

# Loop where k is the last character pressed
k = 0
while (k != ord('q')):

    # Clearing the screen at each loop iteration
    stdscr.clear()

    # All screen border
    stdscr.border(0)

    # Dummy text
    for i in range(10):
        stdscr.addstr(10 + i, 1, "Blah blah blah blah blah blah blah 123 123 123 123")

    # Create a box (Height, Width, y, x) (Positions are top left)
    box1 = curses.newwin(7, 45, 15, 10)
    box1.box()

    # Changing the background color of box
    box1.bkgd(' ', curses.color_pair(1) | curses.A_REVERSE)

    # Add text to box
    # Text is relative (y, x)
    box1.addstr(3, 6, 'Exam paused. To resume press "R"')

    # Dummy text
    for i in range(10):
        stdscr.addstr(21 + i, 1, "Text text text text text text text text text text text text text")

    # Refresh the screen and the box
    stdscr.refresh()
    box1.refresh()

    # Get User input
    k = stdscr.getch()

# Ending curses
curses.endwin()
