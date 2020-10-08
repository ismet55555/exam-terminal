#!/usr/bin/env python

import curses
from pprint import pprint
from time import sleep, time
# from loguru import logger
import yaml
import threading
import logging
import textwrap

# NOTE: https://docs.python.org/2/library/curses.html

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # NOTE: No detailed logs shown when set to "logging.INFO"


class Exam:
    def __init__(self) -> None:
        # Constructor
        self.exam_filepath = "sample_questions.yml"

        self.selection_indicator = "|"
        self.selection_index = 0

        # Loading exam contents
        self.exam_contents = self.__load_parse_examfile(self.exam_filepath)


        self.questions_total = len(self.exam_contents['questions'])
        self.questions_complete = 0
        self.questions_progress = 0

        self.questions_correct = 0
        self.questions_wrong = 0


        self.global_elapsed_time = 0
        self.exam_begin_time = 0
        self.exam_elapsed_time = 0
        self.is_exam_time_out = False

        self.exam_paused = False
        self.exam_paused_elapsed_time = 0

        self.is_timer_timing = False

        logger.info('Exam object created')

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
        self.exam_total_time = self.exam_contents['exam_total_time']
        self.exam_total_time_units = self.exam_contents['exam_total_time_units']

        # TODO: Calculate exam time in seconds? minutes?

        logger.info('Parsing the loaded exam information ...')
        # Loop through all the questions
        for index, question in enumerate(self.exam_contents['questions']):
            # Store the question number
            question['question_number'] = index

            # Create empty list for answer indexes
            question['answer_indexes'] = []
            question['answer_bool'] = []

            # Looping over selection for each question
            for i, s in enumerate(question['selection']):
                
                # Check if a answer was passed with slection
                if isinstance(s, dict):
                    # Get the first key
                    first_key = next(iter(s))

                    # Save the correct answer
                    if s[first_key]:
                        # Is True (correct answer)
                        question['answer_indexes'].append(i)
                        question['answer_bool'].append(True)
                    else:
                        # Is True (incorrect answer)
                        question['answer_bool'].append(False)

                    # Just keep the key
                    question['selection'][i] = first_key

                else:
                    # No value, assumed False answer
                    question['answer_bool'].append(False)

            # Determine if it is a multi-selection question
            question['multiselect'] = sum(question['answer_bool']) > 1
            question['min_selection_count'] = sum(question['answer_bool'])

        # Get the total number of questions
        self.questions_total = len(self.exam_contents['questions'])

        pprint(self.exam_contents)

        return self.exam_contents

    def __basic_screen_setup(self, scr):
        # Hiding the cursor
        curses.curs_set(0)

        # Start colors in curses
        curses.start_color()

        # Define the colors to be used (foreground and background) (ie. curses.color_pair(1))
        #     curses.init_pair(color reference index, font color number, background color number)
        # NOTE:
        #       -1 is transparent
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, 248, curses.COLOR_BLACK)  # Grey

        # Turn off echo
        curses.noecho()

        # Non-blocking for user
        scr.nodelay(True)

    def __draw_screen_border(self, scr, color_pair_index):
        scr.attron(curses.color_pair(color_pair_index))
        scr.border(0)
        scr.attroff(curses.color_pair(color_pair_index))

    def __check_terminal_size(self, scr, height_limit, width_limit) -> bool:
        terminal_size_good = True

        # Getting the screen height and width
        term_height, term_width = scr.getmaxyx()
        
        # Check Height
        if term_height < height_limit:
            scr.addstr(1, 1, f"Terminal height must be more than {height_limit} characters!", curses.color_pair(1))
            terminal_size_good = False

        # Check Width
        if term_width < width_limit:
            scr.addstr(2, 1, f"Terminal width must be more than {width_limit} characters!", curses.color_pair(1))
            terminal_size_good = False

        if terminal_size_good:
            scr.addstr(0, 0, f"[Terminal Size: W:{term_width}, H:{term_height}]", curses.color_pair(1))

        return terminal_size_good

    def __get_message_box_size(self, term_height, term_width, message_lines):
        # Create a box (Height, Width, y, x) (Positions are top left)
        box_height = len(message_lines) + 4
        box_width = int(term_width / 1.5)  # Alternative: len(max(message_lines, key=len)) + 12
        box_y = int(term_height / 2 - box_height / 2)
        box_x = int(term_width / 2 - box_width / 2)
        
        return box_height, box_width, box_y, box_x

    def get_progress_bar(self, exam_progress, bar_char_width=60, bar_char_full='|', bar_char_empty='-') -> str:
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

    def draw_menu(self, scr):
        # Setting up basic stuff for curses
        self.__basic_screen_setup()

        # Non-blocking for user
        scr.nodelay(True)

        # Define keys for this screen
        KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
        KEYS_UP = (curses.KEY_UP, ord('k'))
        KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
        KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))
        KEYS_PAUSE = ord('p')
        KEYS_RESUME = ord('r')
        KEYS_QUIT = ord('q')

        # User key input (ASCII)
        k = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()



        return

    def show_menu(self):
        return curses.wrapper(self.draw_menu)

    ###############################################################################################

    def exam_timer_thread(self):
        while self.is_timer_timing:
            self.global_elapsed_time = time() - self.exam_begin_time 
            if not self.exam_paused:
                # Elapsed exam time
                self.exam_elapsed_time = self.global_elapsed_time - self.exam_paused_elapsed_time 

                # Check if exam time is up
                if self.exam_elapsed_time > self.exam_contents['exam_total_time']:
                    self.is_exam_time_out = True
                    self.is_timer_timing = False
            else:
                # Time Spend paused
                self.exam_paused_elapsed_time = self.global_elapsed_time - self.exam_elapsed_time

    def draw_question(self, scr, question):
        # Setting up basic stuff for curses
        self.__basic_screen_setup(scr)

        # Define keys for this screen
        KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
        KEYS_UP = (curses.KEY_UP, ord('k'))
        KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
        KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))
        KEYS_PAUSE = ord('p')
        KEYS_RESUME = ord('r')
        KEYS_QUIT = ord('q')

        question_x = 8
        selection_x = 10
        start_y = 5

        # Reset selection
        self.selection_index = 0

        # User key input (ASCII)
        k = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            scr.clear()

            ########################################################################################

            # Check user input and adjust the cursor movement
            if k in KEYS_DOWN:
                if not self.exam_paused:
                    self.selection_index += 1

            elif k in KEYS_UP:
                if not self.exam_paused:
                    self.selection_index -= 1

            elif k in KEYS_ENTER:
                if not self.exam_paused:
                    index = self.selection_index
                    correct = question['answer_bool'][self.selection_index]
                    answer = question['selection'][self.selection_index]
                    return index, answer, correct

            elif k == KEYS_PAUSE:
                self.exam_paused = True

            elif k == KEYS_RESUME:
                self.exam_paused = False

            elif k == KEYS_QUIT:
                if not self.exam_paused:
                    break
              
            ########################################################################################

            # Getting the screen height and width
            term_height, term_width = scr.getmaxyx()

            # Check terminal size
            terminal_size_good = self.__check_terminal_size(scr, height_limit=30, width_limit=80)
            if not terminal_size_good:
                pass

            # Drawing the screen border
            self.__draw_screen_border(scr, color_pair_index=6)
            
            ########################################################################################

            # Check if within boundaries of selection indexes
            self.selection_index = max(self.selection_index, 0)
            self.selection_index = min(self.selection_index, len(question['selection']) - 1)

            ########################################################################################

            # Create text wrappers wrapping text over number of characters
            wrapper_question = textwrap.TextWrapper(width=60)
            wrapper_selection = textwrap.TextWrapper(width=40)

            # Wrap and show the question
            question_wrap = wrapper_question.wrap(text=question['question']) 
            for l, line in enumerate(question_wrap):
                scr.addstr(start_y + l - 1, question_x, line)

            # Set the offset to the next line
            selection_offset = len(question_wrap) + 3

            # Wrap and show selection
            for s, selection in enumerate(question['selection']):

                if s == self.selection_index:
                    scr.attron(curses.color_pair(5))

                selection_wrap = wrapper_selection.wrap(text=selection)
                for l, line in enumerate(selection_wrap):
                    scr.addstr(start_y + selection_offset + l - 1, selection_x + 2, line)

                    # Draw selector
                    if s == self.selection_index:
                        scr.addstr(start_y + selection_offset + l - 1, selection_x - 2, self.selection_indicator)

                scr.attroff(curses.color_pair(5))

                # Set the offset to the next line
                selection_offset += len(selection_wrap) + 1

            ########################################################################################

            # Progress bar and status - call method
            scr.attron(curses.color_pair(6))
            progress_bar = self.get_progress_bar(exam_progress=self.questions_progress, bar_char_width=term_width - 23)
            scr.addstr(term_height - 3, 3, f"[ {self.questions_complete:3.0f}  / {self.questions_total:3.0f}  ][{progress_bar}]")

            # Elapsed Time
            progress_bar = self.get_progress_bar(exam_progress=self.exam_elapsed_time / self.exam_contents['exam_total_time'], bar_char_width=term_width - 23)
            scr.addstr(term_height - 2, 3, f"[ {self.exam_elapsed_time:3.0f}s / {self.exam_total_time:3.0f}s ][{progress_bar}]")
            scr.attroff(curses.color_pair(6))

            ########################################################################################

            # Exam pause message box
            scr.nodelay(not self.exam_paused) 
            if self.exam_paused:
                message_lines = ['Exam was paused', 'To resume exam press "R"']
                height, width, y, x = self.__get_message_box_size(term_height, term_width, message_lines)
                pause_box = curses.newwin(height, width, y, x)
                pause_box.box()
                pause_box.border()

                # Add text to box (Text is relative to box -> y, x)
                for l, line in enumerate(message_lines):
                    x = width // 2 - len(line) // 2
                    pause_box.addstr(2 + l, x, line)

            ########################################################################################

            # Check if time has run out on the exam
            if self.is_exam_time_out:
                break

            ########################################################################################

            # Refresh the screen
            scr.refresh()

            # Refresh the pause messgae box
            if self.exam_paused:
                pause_box.refresh()

            # Get User input
            k = scr.getch()

        return -1, 'quit', False

    def show_question(self, question):
        return curses.wrapper(self.draw_question, question)

    ###############################################################################################

    def begin_exam(self):
        logger.info('Exam started')

        self.exam_begin_time = time()

        # Start the independent timer thread for entire exam
        self.is_timer_timing = True
        exam_timer_thread = threading.Thread(target=self.exam_timer_thread, args=())
        exam_timer_thread.daemon = True
        exam_timer_thread.start()

        # TODO: Add option to go back and forth on questions

        for q, question in enumerate(self.exam_contents['questions']):
            # Start timer for current question
            question_elapsed_time = time()

            # Show the question
            index, answer, correct = exam.show_question(question)

            # Exam quit
            if index == -1:
                break

            # Log answer metadata
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

        # Stop independent exam timer
        self.is_timer_timing = False
        exam_timer_thread.join()

        pprint(self.exam_contents)




exam = Exam()
# exam.show_menu()
exam.begin_exam()


