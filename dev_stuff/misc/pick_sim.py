import curses


def draw_menu(stdscr):
    # Predefine and pre-allocate variables
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()

    # Define the colors to be used (ie. curses.color_pair(1))
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Turn off echo
    curses.noecho()

    # Loop where k is the last character pressed
    while (k != ord('q')):
        ###########################################################################################

        # Clearing the screen at each loop iteration
        stdscr.clear()

        # Getting the screen height and term_width
        term_height, term_width = stdscr.getmaxyx()

        # Rendering some text
        whstr = "[Terminal Size: W:{}, H:{}]".format(term_width, term_height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        ###########################################################################################

        # Check user input and adjust the cursor movement
        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        # Check if no user input for some reason
        if k == 0:
            keystr = "No key press detected..."[:term_width - 1]

        # Check for cursor not off the screen in horizontal direction
        cursor_x = max(0, cursor_x)
        cursor_x = min(term_width - 1, cursor_x)

        # Check for cursor not off the screen in vertical direction
        cursor_y = max(0, cursor_y)
        # Excluding status bar at bottom
        cursor_y = min(term_height - 2, cursor_y)

        ###########################################################################################

        # Declaration of strings (ensuring that strings are not larger than screen term_width)
        title = "Question: AWS Certified Architect Practice Exam"[:term_width - 1]
        x = 10
        y = 10
        stdscr.addstr(y, x, title)

        x = 10
        y = 11
        selection = "Written by Ismet Handzic"[:term_width - 1]
        stdscr.addstr(y, x, selection)

        x = 10
        y = 13
        keystr = "Last key pressed: {}".format(k)[:term_width - 1]
        stdscr.addstr(y, x, keystr)

        ###########################################################################################

        # Once the cursor has written everything, move it back to where user specified
        stdscr.move(cursor_y, cursor_x)

        ###########################################################################################

        # Refresh the screen
        stdscr.refresh()

        # Wait for next user input
        k = stdscr.getch()


def main():
    # Calling the curses 'draw_menu' function
    curses.wrapper(draw_menu)

    # ... can add more wrappers here here ...


if __name__ == "__main__":
    # Entry point of code
    main()
