#!/usr/bin/env python

import curses
import logging
import textwrap
import threading
from datetime import datetime
from pprint import pprint
from statistics import mean, median, stdev
from time import sleep, time

import yaml

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)


class Exam:
    def __init__(self, exam_filepath: str) -> None:
        # Loading exam contents
        self.exam_contents = self.__load_parse_examfile(exam_filepath)

        self.color = {}
        self.decor = {}

        self.height_limit = 27
        self.width_limit = 85
        self.terminal_size_good = True

        self.questions_total = len(self.exam_contents['questions'])
        self.questions_complete = 0
        self.questions_progress = 0

        self.questions_correct = 0
        self.questions_wrong = 0

        self.selection_indicator = "|"
        self.selection_index = 0

        self.global_elapsed_time = 0
        self.exam_begin_time = 0
        self.exam_elapsed_time = 0
        self.is_exam_time_out = False

        self.exam_paused = False
        self.exam_paused_elapsed_time = 0
        self.exam_paused_count = 0

        self.exam_quit = False
        self.exam_exit = False  # Straight exit entire program

        self.is_timer_timing = False

        logger.info('Exam was created and exam file loaded')

    ###############################################################################################

    def __load_parse_examfile(self, filepath: str) -> dict:
        # Load the examp file
        logger.info(f"Loading specified exam file: '{filepath}' ...")
        try:
            with open(filepath) as file:
                self.exam_contents = yaml.load(file, Loader=yaml.FullLoader)
        except Exception as e:
            logger.error(f"Failed to load specified exam file: '{filepath}'")
            return False

        # Get the total exam time
        self.exam_allowed_time = self.exam_contents['exam']['exam_allowed_time']
        self.exam_allowed_time_units = self.exam_contents['exam']['exam_allowed_time_units']

        # TODO: Calculate exam time in seconds? minutes?

        logger.info('Parsing the loaded exam information ...')
        # Loop through all the questions
        for index, question in enumerate(self.exam_contents['questions']):
            # Store the question number
            question['question_number'] = index

            # Create empty list for answer indexes
            question['question_answer_indexes'] = []
            question['question_answer_bool'] = []

            # Looping over selection for each question
            for i, s in enumerate(question['selection']):
                
                # Check if a answer was passed with slection
                if isinstance(s, dict):
                    # Get the first key
                    first_key = next(iter(s))

                    # Save the correct answer
                    if s[first_key]:
                        # Is True (correct answer)
                        question['question_answer_indexes'].append(i)
                        question['question_answer_bool'].append(True)
                    else:
                        # Is True (incorrect answer)
                        question['answer_bool'].append(False)

                    # Just keep the key
                    question['selection'][i] = first_key

                else:
                    # No value, assumed False answer
                    question['question_answer_bool'].append(False)

            # Determine if it is a multi-selection question
            question['question_multiselect'] = sum(question['question_answer_bool']) > 1
            question['question_min_selection_count'] = sum(question['question_answer_bool'])

            # Set answered status
            question['answered'] = False

        # Get the total number of questions
        self.exam_contents['exam']['exam_questions_count'] = len(self.exam_contents['questions'])

        return self.exam_contents

    def __basic_screen_setup(self, scr):
        # Hiding the cursor
        curses.curs_set(0)

        # Load curses colors
        self.color, self.decor = self.__load_curses_colors_decor()

        # Turn off echo
        curses.noecho()

        # Non-blocking for user
        scr.nodelay(True)

    def __draw_screen_border(self, scr, color) -> None:
        scr.attron(color)
        scr.border(0)
        scr.attroff(color)

    def __draw_horizontal_sceen_seperator(self, scr, y, color) -> None:
        # Getting the screen height and width
        term_height, term_width = scr.getmaxyx()

        if y < term_height - 2 and y > 1:
            for x in range(term_width - 2):
                scr.addstr(y, x + 1, '-', color)

    def __check_terminal_size(self, scr) -> None:
        # Getting the screen height and width
        term_height, term_width = scr.getmaxyx()
        
        # Check Height and width
        self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

        scr.addstr(1, 1, f"[Terminal Size: W:{term_width}, H:{term_height}]", self.color['grey-light'])

        scr.nodelay(self.terminal_size_good) 
        k = 0
        KEYS = self.__load_keys()
        while not self.terminal_size_good:
            if k in KEYS['QUIT']:
                self.exam_exit = True
                break

            # Re-evaluate the screen size
            term_height, term_width = scr.getmaxyx()
            self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

            # if not self.exam_paused and not self.exam_quit:
            message_lines = [
                'Uh-Oh! Window size too small!',
                '',
                f'Current size is W:{term_width} by H:{term_height}',
                f'Size must be at least W:{self.width_limit} by H:{self.height_limit}',
                '',
                'Please resize window to continue',
                ''
                'To quit program press "Q" or "ESC"'
                ]
            # self.__show_message_box(scr, message_lines)
            for y, line in enumerate(message_lines):
                scr.addstr(1 + y, 1, line, self.decor['bold'])

            scr.refresh()
            k = scr.getch()

    def __get_message_box_size(self, term_height, term_width, message_lines):
        # Create a box (Height, Width, y, x) (Positions are top left)
        box_height = len(message_lines) + 4
        box_width = int(term_width / 1.5)  # Alternative: len(max(message_lines, key=len)) + 12
        box_y = int(term_height / 2 - box_height / 2)
        box_x = int(term_width / 2 - box_width / 2)
        
        return box_height, box_width, box_y, box_x

    def __show_message_box(self, scr, message_lines: list) -> None:
        term_height, term_width = scr.getmaxyx()

        height, width, y, x = self.__get_message_box_size(term_height, term_width, message_lines)
        message_box = curses.newwin(height, width, y, x)
        message_box.box()
        message_box.border()

        for l, line in enumerate(message_lines):
            # Add text each line to box (Text is relative to box -> y, x)
            x = width // 2 - len(line) // 2
            y = l + 2
            message_box.addstr(y, x, line)

        # Refresh the messgae box
        message_box.refresh()

    def __get_progress_bar(self, exam_progress, bar_char_width=60, bar_char_full='|', bar_char_empty='-') -> str:
        progress_str = []
        for i in range(bar_char_width):
            # TODO: Different colors for different parts of the progress bar somehow
            if i <= exam_progress * bar_char_width:
                progress_str.append(bar_char_full)
            else:
                progress_str.append(bar_char_empty)

        progress_str = "".join(progress_str)
        return progress_str

    ###############################################################################################

    @staticmethod
    def __load_curses_colors_decor() -> tuple:
        # In code usage example:
        #       scr.addstr(y, x, "hello", self.color['blue'])
        #       scr.addstr(y, x, "hello", self.color['blue'] | self.decor['bold'])

        # Start colors in curses
        try: curses.start_color()
        except: pass

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

        # Initiating curses color and saving for quick reference
        color = {}
        for index, (key, value) in enumerate(color_definition.items()):
            curses.init_pair(index + 1, value[0], value[1])
            color[key] = curses.color_pair(index + 1)

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

    @staticmethod
    def __load_keys():
        KEYS = {
            "ENTER": (curses.KEY_ENTER, ord('\n'), ord('\r')),
            "SPACE": (32, ord(' ')),
            "UP": (curses.KEY_UP, ord('k')),
            "DOWN": (curses.KEY_DOWN, ord('j')),
            "RIGHT": (curses.KEY_RIGHT, ord('l')),
            "LEFT": (curses.KEY_LEFT, ord('h')),
            "PAUSE": (ord('p'), ord('P')),
            "RESUME": (ord('r'), ord('R')),
            "QUIT": (27 , ord('q'), ord('Q'))
        }
        return KEYS

    @staticmethod
    def __load_software_ascii_name() -> list:
        # TODO: Do something with this, probably not needed
        software_name = [
            " _____        _   _            _____              _         _ ",
            "|_   _|__ ___| |_|_|___ ___   |_   _|__ ___ _____|_|___ ___| |",
            "  | || -_|_ -|  _| |   | . |    | || -_|  _|     | |   | .'| |",
            "  |_||___|___|_| |_|_|_|_  |    |_||___|_| |_|_|_|_|_|_|__,|_|",
            "                       |___|                                  ",
        ]
        return software_name

    @staticmethod
    def __center_x(display_width, line) -> int:
        return display_width // 2 - len(line) // 2

    @staticmethod
    def __center_y(display_height) -> int:
        return display_height // 2

    ###############################################################################################

    def draw_menu(self, scr) -> bool:
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr)
        KEYS = self.__load_keys()

        # User key input (ASCII)
        k = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user keyboard input
            if k in KEYS['DOWN'] or k in KEYS['RIGHT']:
                self.selection_index += 1

            elif k in KEYS['UP'] or k in KEYS['LEFT']:
                self.selection_index -= 1

            elif k in KEYS['ENTER']:
                if self.selection_index == 0:
                    # TODO: Prompt or countdown?
                    return True
                elif self.selection_index == 1:
                    # TODO: Are you sure prompt
                    return False

            elif k in KEYS['QUIT']:
                # TODO: Are you sure prompt
                return False

            ########################################################################################

            term_height, term_width = scr.getmaxyx()          

            ########################################################################################

            # Check terminal size
            self.__check_terminal_size(scr)
            scr.nodelay(self.terminal_size_good)

            # Drawing the screen border
            self.__draw_screen_border(scr, self.color['grey-dark'])

            ########################################################################################

            # Show software name/title
            scr.addstr(term_height - 2, 2, "Testing Terminal v0.1", self.color['grey-dark'])

            ########################################################################################

            wrapper_menu_item = textwrap.TextWrapper(width=term_width - 25)

            start_y = 2
            start_x = [5, 22]

            line = f"{self.exam_contents['exam']['exam_title']}"
            scr.addstr(start_y, self.__center_x(term_width, line), line, self.decor['bold'])
            start_y += 1

            line = f"{self.exam_contents['exam']['exam_author']}"
            scr.addstr(start_y, self.__center_x(term_width, line), line, self.color['grey-light'])
            start_y += 1

            line = f"{self.exam_contents['exam']['exam_edit_date']}"
            scr.addstr(start_y, self.__center_x(term_width, line), line, self.color['grey-light'])
            start_y += 3


            lines = ["Description:", f"{self.exam_contents['exam']['exam_description']}"]
            menu_item_wrap = ' '
            for x, line_text in zip(start_x, lines):
                menu_item_wrap = wrapper_menu_item.wrap(text=line_text)
                for l, line in enumerate(menu_item_wrap):
                    scr.addstr(start_y + l - 1, x, line, self.color['default'])
            start_y += len(menu_item_wrap)

            
            lines = ["Exam Type:", f"Multiple Choice, Single Answer"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y , x, line, self.color['default'])
            start_y += 2

            lines = ["Questions:", f"52"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            lines = ["Allowed Time:", f"{self.exam_contents['exam']['exam_allowed_time']} {self.exam_contents['exam']['exam_allowed_time_units']}"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            lines = ["Passing Score:", f"{self.exam_contents['exam']['exam_passing_score']} %"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            ########################################################################################

            y_selection = term_height - 9

            selections = ["Begin Exam","Quit"]

            # Check if within boundaries of selection indexes
            self.selection_index = max(self.selection_index, 0)
            self.selection_index = min(self.selection_index, len(selections) - 1)

            # Get the x position of selection indicator
            longest_selection_text = len(max(selections, key = len))
            x_begin = term_width // 2 - longest_selection_text // 2 - 3
            x_end = term_width // 2 + longest_selection_text // 2 + 2

            y = 4

            for s, selection in enumerate(selections):
                if s == self.selection_index:
                    # Color for highlighted selection text
                    color = self.color['default'] | self.decor['bold']
                    scr.addstr(y + s + 1 + y_selection, x_begin, '|', color)
                    scr.addstr(y + s + 1 + y_selection, x_end, '|', color)
                else:
                    color = self.color['grey-light']
                scr.addstr(y + s + 1 + y_selection, term_width // 2 - len(selection) // 2, selection, color)

            ########################################################################################

            # Horizontal Seperator
            self.__draw_horizontal_sceen_seperator(scr, term_height - 6, self.color['grey-dark'])

            ########################################################################################

            # Straight exist software
            if self.exam_exit:
                exit()

            ########################################################################################

            # Refresh the screen
            scr.refresh()

            # Get User input
            k = scr.getch()

    def show_menu(self) -> bool:
        return curses.wrapper(self.draw_menu)

    ###############################################################################################

    def exam_timer_thread(self):
        # FIXME: Account for terminal size message error
        while self.is_timer_timing:
            self.global_elapsed_time = time() - self.exam_begin_time 
            if not self.exam_paused:
                # Elapsed exam time
                self.exam_elapsed_time = self.global_elapsed_time - self.exam_paused_elapsed_time 

                # Check if exam time is up
                if self.exam_elapsed_time > self.exam_contents['exam']['exam_allowed_time']:
                    self.is_exam_time_out = True
                    self.is_timer_timing = False
            else:
                # Time Spend paused
                self.exam_paused_elapsed_time = self.global_elapsed_time - self.exam_elapsed_time

    def draw_question(self, scr, question):
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr)
        KEYS = self.__load_keys()

        start_y = 3
        question_x = 4
        selection_x = 6
        self.selection_index = 0

        # User key input (ASCII)
        k = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user keyboard input
            if k in KEYS['DOWN']:
                if not self.exam_paused and not self.is_exam_time_out:
                    self.selection_index += 1

            elif k in KEYS['UP']:
                if not self.exam_paused and not self.is_exam_time_out:
                    self.selection_index -= 1

            elif k in KEYS['ENTER']:
                if self.is_exam_time_out:
                    return -1, 'quit', False

                elif not self.exam_paused:
                    index = self.selection_index
                    correct = question['question_answer_bool'][self.selection_index]
                    answer = question['selection'][self.selection_index]

                    # Return the entered answer
                    return index, answer, correct

            elif k in KEYS['PAUSE']:
                self.exam_paused = True
                self.exam_paused_count += 1

            elif k in KEYS['RESUME']:
                self.exam_paused = False
                self.exam_quit = False

            elif k in KEYS['QUIT']:
                if not self.is_exam_time_out:
                    self.exam_quit += 1
              
            ########################################################################################

            # Check terminal size
            terminal_size_good = self.__check_terminal_size(scr)
            scr.nodelay(self.terminal_size_good)  # TODO: Move to one location ...

            # Drawing the screen border
            self.__draw_screen_border(scr, self.color['grey-dark'])
            
            ########################################################################################

            # Check if within boundaries of selection indexes
            self.selection_index = max(self.selection_index, 0)
            self.selection_index = min(self.selection_index, len(question['selection']) - 1)

            ########################################################################################

            # Create text wrappers wrapping text over number of characters
            term_height, term_width = scr.getmaxyx()
            wrapper_question = textwrap.TextWrapper(width=term_width - 5)
            wrapper_selection = textwrap.TextWrapper(width=term_width - 10)

            # Wrap and show the question
            question_wrap = wrapper_question.wrap(text=question['question']) 
            for l, line in enumerate(question_wrap):
                scr.addstr(start_y + l - 1, question_x, line, self.color['default'] | self.decor['bold'])

            self.__draw_horizontal_sceen_seperator(scr, len(question_wrap) + 3, self.color['grey-dark'])


            # Set the offset to the next line
            selection_offset = len(question_wrap) + 3

            # Wrap and show selection
            for s, selection in enumerate(question['selection']):

                selection_wrap = wrapper_selection.wrap(text=selection)
                for l, line in enumerate(selection_wrap):
                    # Style selection and draw selector
                    if s == self.selection_index:
                        color = self.color['default'] | self.decor['bold']

                        # Get the x position of selection indicator
                        # longest_selection_text = len(max(question['selection'], key = len))

                        # Draw the indicators
                        scr.addstr(start_y + selection_offset + l - 1, selection_x - 2, self.selection_indicator, self.color['default'] | self.decor['bold'])
                        # scr.addstr(start_y + selection_offset + l - 1, selection_x + longest_selection_text + 4, self.selection_indicator, color)
                    else:
                        color = self.color['grey-light']

                    scr.addstr(start_y + selection_offset + l - 1, selection_x + 2, line, color)


                # Set the offset to the next line
                selection_offset += len(selection_wrap) + 1

            ########################################################################################

            # Getting the screen height and width
            term_height, term_width = scr.getmaxyx()

            # Progress bar and status - call method
            progress_bar = self.__get_progress_bar(exam_progress=self.questions_progress, bar_char_width=term_width - 23)
            scr.addstr(term_height - 3, 3, f"[ {self.questions_complete:3.0f}  / {self.questions_total:3.0f}  ][{progress_bar}]", self.color['default'])

            # Elapsed Time
            examp_elapsed_dec = self.exam_elapsed_time / self.exam_contents['exam']['exam_allowed_time']
            color = self.color['default']
            if examp_elapsed_dec > 0.85 and examp_elapsed_dec <= 0.95:
                color = self.color['orange']
            if examp_elapsed_dec > 0.92:
                color = self.color['red'] | self.decor['bold']
            progress_bar = self.__get_progress_bar(exam_progress=examp_elapsed_dec, bar_char_width=term_width - 23)
            scr.addstr(term_height - 2, 3, f"[ {self.exam_elapsed_time:3.0f}s / {self.exam_allowed_time:3.0f}s ][{progress_bar}]", color)

            ########################################################################################

            # Refresh the main screen layout
            scr.refresh()

            ########################################################################################

            # If prompts are shown, ensure that no nodelay is False, and vice versa
            scr.nodelay(not any([self.exam_paused, self.exam_quit, self.is_exam_time_out])) 

            # Exam pause message box
            if self.exam_paused and not self.exam_quit:
                message_lines = ['Exam was paused', 'To resume exam press "R"']
                self.__show_message_box(scr, message_lines)

            # Exam quit message box
            if self.exam_quit:
                self.exam_paused = True
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To resume exam press "R"']
                self.__show_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.exam_quit > 1:
                    break

            # Straight exist software
            if self.exam_exit:
                exit()

            # Exam timed out message box
            if self.is_exam_time_out:
                message_lines = ['Exam time has expired', 'Press "ENTER" to evalute']
                self.__show_message_box(scr, message_lines)

            # TODO:  Only use a exit flag instead of break to outsource the checking (ensure loop is completed)

            ########################################################################################

            # Get User input
            k = scr.getch()

        return -1, 'quit', False

    def show_question(self, question):
        return curses.wrapper(self.draw_question, question)

    ###############################################################################################

    def draw_result(self, scr):
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr)
        KEYS = self.__load_keys()

        self.selection_index = 0

        # User key input (ASCII)
        k = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user keyboard input
            if k in KEYS['DOWN'] or k in KEYS['RIGHT']:
                self.selection_index += 1

            elif k in KEYS['UP'] or k in KEYS['LEFT']:
                self.selection_index -= 1

            elif k in KEYS['ENTER']:
                if self.selection_index == 0:
                    # TODO: Prompt or countdown?
                    return True
                elif self.selection_index == 1:
                    # TODO: Are you sure prompt
                    return False

            elif k in KEYS['QUIT']:
                # TODO: Are you sure prompt
                return False

            ########################################################################################

            term_height, term_width = scr.getmaxyx()          

            ########################################################################################

            # Check terminal size
            terminal_size_good = self.__check_terminal_size(scr)
            scr.nodelay(self.terminal_size_good)  # TODO: Move to one location

            # Drawing the screen border
            self.__draw_screen_border(scr, self.color['grey-dark'])

            ########################################################################################

            # TODO
            #   - Selections
            #       - Review Questions
            #       - Print
            #       - Main Menu
            #       - Quit

            start_y = 2

            # Heading
            line = f"Exam Result Summary"
            scr.addstr(start_y, self.__center_x(term_width, line), line, self.decor['bold'])
            start_y += 2

            self.__draw_horizontal_sceen_seperator(scr, start_y, self.color['grey-dark'])
            start_y += 2

            start_x = [4, 30]
            results = self.__assemble_exam_results()
            for index, item in results.items():
                scr.addstr(start_y , start_x[0], item['label'], self.color['default'])
                scr.addstr(start_y , start_x[1], item['text'], self.color[item['color']] | self.decor[item['decor']])
                start_y += item['skip_lines']

            ########################################################################################

            # Straight exist software
            if self.exam_exit:
                exit()

            ########################################################################################

            # Refresh the screen
            scr.refresh()

            # Get User input
            k = scr.getch()

    def __evaluate_exam(self):
        questions_count = len(self.exam_contents['questions'])

        # Get the score
        self.exam_contents['exam']['evaluation_percent'] = (self.questions_correct / questions_count) * 100

        # Get the score label/text
        if self.exam_contents['exam']['evaluation_percent'] >= self.exam_contents['exam']['exam_passing_score']:
            self.exam_contents['exam']['evaluation_label'] = "PASSED"
        else:
            self.exam_contents['exam']['evaluation_label'] = "FAILED"

    def __assemble_exam_results(self) -> dict:
        results = {}

        index = 0

        results[index] = {
            "label": "Exam Title:",
            "text": self.exam_contents['exam']['exam_title'],  # TODO: Wrap or truncate
            "color": "default",
            "decor": "bold",
            "x_pos": [4, 30],
            "skip_lines": 1
        }
        index += 1


        results[index] = {
            "label": "Result:",
            "text": self.exam_contents['exam']['evaluation_label'],
            "color": "blue",
            "decor": "bold",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        results[index] = {
            "label": "Correct:",
            "text": f"{self.exam_contents['exam']['evaluation_percent']:3.1f}% ({self.questions_correct} of {self.exam_contents['exam']['exam_questions_count']})",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        # results[index] = {
        #     "label": "Incorrect:",
        #     "text": f"{100 - self.exam_contents['exam']['evaluation_percent']:3.1f}% ({self.exam_contents['exam']['exam_questions_count'] - self.questions_correct} of {self.exam_contents['exam']['exam_questions_count']})",
        #     "color": "default",
        #     "decor": "normal",
        #     "x_pos": [4, 35],
        #     "skip_lines": 1
        # }
        # index += 1


        answered = 0
        for question in self.exam_contents['questions']:
            if question['answered']:
                answered += 1
        results[index] = {
            "label": "Questions Answered:",
            "text": f"{answered} of {self.exam_contents['exam']['exam_questions_count']}",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        results[index] = {
            "label": "Exam Complete Time:",
            "text": f"{self.exam_elapsed_time:3.1f} seconds",  # TODO: Convert to hr, min, sec
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        exam_begin_time = datetime.fromtimestamp(self.exam_contents['exam']['exam_begin_timestamp']).strftime("%m/%d/%Y %H:%M:%S")
        exam_end_time = datetime.fromtimestamp(self.exam_contents['exam']['exam_end_timestamp']).strftime("%m/%d/%Y, %H:%M:%S")
        results[index] = {
            "label": "Exam Time Range:",
            "text": f"{exam_begin_time} -> {exam_end_time}",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 2
        }
        index += 1


        results[index] = {
            "label": "Number of Times Paused:",
            "text": str(self.exam_paused_count),
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        results[index] = {
            "label": "Elapsed Pauseed Time:",
            "text": f"{self.exam_paused_elapsed_time:3.1f} seconds",  # TODO: Convert to hr, min, sec
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        # answer_distribution = ""
        # for question in self.exam_contents['questions']:
        #     if question['answered']:
        #         if question['answered_correctly']:
        #             answer_distribution += ' +'
        #         else:
        #             answer_distribution += ' -'
        # results[index] = {
        #     "label": "Answers Per Question:",
        #     "text": f"[First]{answer_distribution} [Last]",
        #     "color": "default",
        #     "decor": "normal",
        #     "x_pos": [4, 35],
        #     "skip_lines": 2
        # }
        # index += 1


        width = 35
        answer_distribution = ['.'] * width
        for question in self.exam_contents['questions']:
            if question['answered']:
                answer_distribution[int((question['answered_exam_time'] / self.exam_elapsed_time) * width) - 1] = "x"
        results[index] = {
            "label": "Answers Over Exam Time:",
            "text": f"[ 0.0s ]{''.join(answer_distribution)}[ {self.exam_elapsed_time:.1f}s ]",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1


        answer_times = []
        for question in self.exam_contents['questions']:
            if question['answered']:
                answer_times.append(question['answered_question_time'])


        end_time = max(answer_times) * 1.25
        width = 35
        answer_distribution = ['.'] * width
        for answer_time in answer_times:
            answer_distribution[int((answer_time / end_time) * width) - 1] = "x"

        results[index] = {
            "label": "Answer Times:",
            "text": f"[ 0.0s ]{''.join(answer_distribution)}[ {end_time:.1f}s ]",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label": "Average Time Per Answer:",
            "text": f"{mean(answer_times):.1f} +/- {stdev(answer_times):.2f} seconds",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label": "Median Time Per Answer:",
            "text": f"{median(answer_times):.1f} seconds",
            "color": "default",
            "decor": "normal",
            "x_pos": [4, 35],
            "skip_lines": 1
        }
        index += 1

        return results

    def show_result(self):
        return curses.wrapper(self.draw_result)

    ###############################################################################################

    def begin_exam(self):
        logger.info('Exam started')

        self.exam_begin_time = time()
        self.exam_contents['exam']['exam_begin_timestamp'] = self.exam_begin_time

        # Start the independent timer thread for entire exam
        self.is_timer_timing = True
        exam_timer_thread = threading.Thread(target=self.exam_timer_thread, args=())
        exam_timer_thread.daemon = True
        exam_timer_thread.start()

        # TODO: Add option to go back and forth on questions

        for q, question in enumerate(self.exam_contents['questions']):
            # Start timer for current question
            question_elapsed_time = time()
            self.exam_contents['questions'][q]['question_presented_timestamp'] = question_elapsed_time

            # Show the question
            index, answer, correct = exam.show_question(question)

            # Exam quit
            if index == -1:
                break

            # Log answer metadata
            self.exam_contents['questions'][q]['answered'] = True
            self.exam_contents['questions'][q]['answered_timestamp'] = time()
            self.exam_contents['questions'][q]['answered_exam_time'] = self.exam_elapsed_time
            self.exam_contents['questions'][q]['answered_question_time'] = time() - question_elapsed_time
            self.exam_contents['questions'][q]['answered_correctly'] = correct

            # Increment correct or wrong answer
            if correct:
                self.questions_correct += 1
            else:
                self.questions_wrong += 1

            # Increment questions compelted
            self.questions_complete += 1

            # Calculate Progress
            self.questions_progress = (self.questions_complete / self.questions_total)


        self.exam_contents['exam']['exam_end_timestamp'] = time()

        # Stop independent exam timer
        self.is_timer_timing = False
        exam_timer_thread.join()

        # Evaluate the exam
        self.__evaluate_exam()

        # pprint(self.exam_contents)
        # exit()



exam = Exam(exam_filepath="exam.yml")
menu_result = exam.show_menu()
if menu_result:
    exam.begin_exam()

    exam.show_result()
