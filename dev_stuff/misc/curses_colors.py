#!/usr/bin/env python3

import curses


def main(stdscr):
    print(curses.has_colors())

    curses.start_color()
    curses.use_default_colors()

    for i in range(0, 255):
        # (color index, font color number, background color number)
        curses.init_pair(i + 1, i, -1)
    try:
        for i in range(0, 255):
            print(i, str(i))
            stdscr.addstr(str(i) + ', ', curses.color_pair(i))
            stdscr.refresh()

    except curses.ERR:
        # End of screen reached
        pass
    finally:
        stdscr.getch()


curses.wrapper(main)
