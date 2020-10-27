import curses
import logging
from pprint import pprint
from typing import Dict, Tuple


logger = logging.getLogger()


def load_curses_colors_decor() -> Tuple[dict, dict]:
    # In code usage example:
    #       scr.addstr(y, x, "hello", self.color['blue'])
    #       scr.addstr(y, x, "hello", self.color['blue'] | self.decor['bold'])

    # Start colors in curses
    curses.start_color()

    # Defining colors [foreground/font, background]
    color_definition = {
        'default':      [curses.COLOR_WHITE, 0],    # FIXME: Rename to "normal" to match decor
        'red':          [curses.COLOR_RED, 0],
        'green':        [curses.COLOR_GREEN, 0],
        'blue':         [curses.COLOR_BLUE, 0],
        'yellow':       [curses.COLOR_YELLOW, 0],
        'orange':       [209, 0],
        'cyan':         [curses.COLOR_CYAN, 0],
        'magenta':      [curses.COLOR_MAGENTA, 0],
        'grey-dark':    [240, 0],
        'grey-light':   [248, 0],
        'black-white':  [curses.COLOR_BLACK, curses.COLOR_WHITE],
        'white-red':    [curses.COLOR_WHITE, curses.COLOR_RED]
    }

    # If terminal does not support colors, reset everything to white
    if not curses.has_colors() or not curses.can_change_color():
        for color in color_definition:
            color_definition[color] = [curses.COLOR_WHITE, 0]

    # Initiating curses color and saving for quick reference
    color = {}
    for index, (key, value) in enumerate(color_definition.items()):
        try:
            curses.init_pair(index + 1, value[0], value[1])
        except:
            curses.init_pair(index + 1, 0, 0)
        color[key] = curses.color_pair(index + 1)

    # Defining font decorations
    decoration_definition ={
        'normal' : curses.A_NORMAL,         # Normal display (no highlight)
        'standout': curses.A_STANDOUT,      # Best highlighting mode of the terminal
        'underline': curses.A_UNDERLINE,    # Underlining
        'reverse': curses.A_REVERSE,        # Reverse video
        'blink': curses.A_BLINK,            # Blinking
        'dim': curses.A_DIM,                # Half bright
        'bold': curses.A_BOLD,              # Extra bright or bold
        'protect': curses.A_PROTECT,        # Protected mode
        'invisible': curses.A_INVIS,        # Invisible or blank mode
        'alt-char': curses.A_ALTCHARSET,    # Alternate character set
        'char': curses.A_CHARTEXT           # Bit-mask to extract a character
    }

    # Initiating curses color and saving for quick reference
    decor = {}
    for key, value in decoration_definition.items():
        decor[key] = value

    return color, decor


def load_keys() -> dict:
    KEYS = {
        "ENTER":  (curses.KEY_ENTER, ord('\n'), ord('\r')),
        "SPACE":  (32, ord(' ')),
        "UP":     (curses.KEY_UP, ord('k')),
        "DOWN":   (curses.KEY_DOWN, ord('j')),
        "RIGHT":  (curses.KEY_RIGHT, ord('l')),
        "LEFT":   (curses.KEY_LEFT, ord('h')),
        "PAUSE":  (ord('p'), ord('P')),
        "RESUME": (ord('r'), ord('R')),
        "QUIT":   (27 , ord('q'), ord('Q'))
    }
    return KEYS


def load_software_ascii_name() -> str:
    # TODO: Smarter, automatic loading of version
    
    software_name = "Exam Terminal"
    software_version = "0.0.4"  # TODO: Pull from setup.py somehow
    return software_name + ' v' + software_version


def center_x(display_width:int, line:str) -> int:
    return display_width // 2 - len(line) // 2


def center_y(display_height:int) -> int:
    return display_height // 2


def truncate_text(text:str, length:int) -> str:
    truncated_text = text
    if len(text) >= length - 3:
        truncated_text = text[0:length - 3] + '...'

    return truncated_text


def get_message_box_size(term_height:int, term_width:int, message_lines:list) -> Tuple[int, int, int, int]:
    """
    Given a message box list with each item being a message box line/row,
    this method find the right size and position of the message box for 
    the given terminal size

    Parameters:
        term_height (int)    : Number of rows/lines in terminal
        term_width (int)     : Number of columns in terminal
        message_lines (list) : Lines of text in each list item
    Returns: 
        box_height (int) : Height of message box (rows/lines) 
        box_width (int)  : Width of message box (columns)
        box_y (int)      : Vertical position of box in terminal
        box_x (int)      : Horizontal position of box in terminal
    """
    box_height = len(message_lines) + 4
    box_width = int(term_width / 1.5)  # Alternative: len(max(message_lines, key=len)) + 12
    box_y = term_height // 2 - box_height // 2
    box_x = term_width // 2 - box_width // 2
    
    return box_height, box_width, box_y, box_x


def get_progress_bar(exam_progress: float, bar_char_width=60, bar_char_full='|', bar_char_empty='-') -> str:
    """
    Make a progress bar with specified parameters

    Parameters:
        exam_progress (float) : Exam progress from 0 to 1 (ie. 0.45 is 45%)
        bar_char_width (int)  : Total width of progress bar, columns of text
        bar_char_full (str)   : Symbol for filled
        bar_char_empty (str)  : Symbol for empty
    Returns: 
        (str) : Progress bar as text
    """
    # TODO: Different colors for different parts of the progress bar somehow

    progress_str = []
    for i in range(bar_char_width):
        
        if i <= exam_progress * bar_char_width:
            progress_str.append(bar_char_full)
        else:
            progress_str.append(bar_char_empty)

    progress_str = "".join(progress_str)
    return progress_str


def draw_screen_border(scr, color:list) -> None:
    """
    Draw a border around entire terminal screen with specified color

    Parameters:
        scr (obj)   : Handle for curses terminal screen handle
        color (list): Foreground and background color (ie. [250, 0])
    Returns: 
        None
    """
    scr.attron(color)
    scr.border(0)
    scr.attroff(color)


def draw_horizontal_seperator(scr, y:int, color:list) -> None:
    """
    Draw a horizontal line accross the terminal screen at specified height
    and with specified color

    Parameters:
        scr (obj)   : Handle for curses terminal screen handle
        y (int)     : The line/row number from top of the screen
        color (list): Foreground and background color (ie. [250, 0])
    Returns: 
        None
    """
    scr.attron(color)
    scr.border(0)
    scr.attroff(color)
    # Getting the screen height and width
    term_height, term_width = scr.getmaxyx()

    if y < term_height - 2 and y > 1:
        for x in range(term_width - 2):
            scr.addstr(y, x + 1, '-', color)


def draw_vertical_seperator(scr, x:int, color:list) -> None:
    """
    Draw a vertical line accross the terminal screen at specified character
    column and with specified color

    Parameters:
        scr (obj)   : Handle for curses terminal screen handle
        x (int)     : The column number from left of the screen
        color (list): Foreground and background color (ie. [250, 0])
    Returns: 
        None
    """
    # Getting the screen height and width
    term_height, term_width = scr.getmaxyx()

    # TODO: Currently unused but may come in handy
