#!/usr/bin/env python3

import curses
import logging
import os
import sys
import textwrap
import threading
from datetime import datetime
from statistics import mean, median, stdev
from time import gmtime, strftime, time
from typing import Dict, Tuple

from fpdf import FPDF

from exam_terminal import utility

logger = logging.getLogger()


class ExamTerminal:
    """This class defines the exam terminal and its function."""

    def __init__(self, exam_file_contents: dict, exam_attempt: int = 0) -> None:
        """
        Object constructor method

        Parameters:
            exam_file_contents (dict): Pre-loaded exam contents
        Returns:
            None
        """
        # Defining all possible exam type descriptions
        self.exam_types = {0: "Multiple Choice, Single Answer", 1: "Multiple Choice, Multiple Answers"}

        # Parse exam contents
        self.exam_contents = {}
        self.exam_contents = self.__parse_examfile_contents(exam_file_contents, exam_attempt)

        self.color = {}
        self.decor = {}

        self.halfdelay_screen_refresh = 5  # 10th of a second

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

        self.exam_quit = 0
        self.exam_exit = False  # Straight exit entire program

        self.is_timer_timing = False

    ###############################################################################################

    def __parse_examfile_contents(self, exam_file_contents: dict, exam_attempt: int) -> Dict:
        """
        Parsing and supplementing a exam file contents

        Parameters:
            exam_file_contents (dict): Pre-loaded exam contents
        Returns:
            return (Dict): Loaded and parsed info of exam file contents
        """
        logger.debug(f"Parsing the loaded exam file ...")

        # Get the exam allowed time in seconds
        if exam_attempt < 1:
            # FIXME: Should not have to use "exam_attempt" to make this work.
            logger.debug(f"Calculating exam_allwed_time ...")
            exam_file_contents['exam']['exam_allowed_time'] = utility.to_seconds(
                exam_file_contents['exam']['exam_allowed_time'], exam_file_contents['exam']['exam_allowed_time_units'])
        # Save the current exam attempt
        exam_file_contents['exam']['exam_attempt'] = exam_attempt

        # Default exam type. If any questions are multiple answers, change type
        exam_file_contents['exam']['exam_type'] = self.exam_types[0]

        logger.debug(f"Loading {len(exam_file_contents['questions'])} questions ...")
        # Loop through all the questions
        for index, question in enumerate(exam_file_contents['questions']):
            # Store the question number
            question['question_number'] = index

            # Create empty list for answer indexes
            question['question_answer_indexes'] = []
            question['question_answer_bool'] = []

            # Looping over selection for each question
            for i, s in enumerate(question['selection']):
                # Check if a answer was passed with selection
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

            # Change exam type
            if question['question_multiselect']:
                exam_file_contents['exam']['exam_type'] = self.exam_types[1]

            # Set answered status
            question['answered'] = False

        # Get the total number of questions
        exam_file_contents['exam']['exam_questions_count'] = len(exam_file_contents['questions'])

        logger.debug('Successfully parsed exam information from file')

        return exam_file_contents

    def __basic_screen_setup(self, scr, halfdelay: bool) -> None:
        """
        Basic configurations of the current curses terminal screen

        Parameters:
            scr (obj)      : Handle for curses terminal screen handle
            halfdely (bool): If True, refresh specified 1/10th of second, else refresh 25.5 seconds
        Returns:
            None
        """
        # Hiding the cursor
        curses.curs_set(0)

        # Load curses colors
        self.color, self.decor = utility.load_curses_colors_decor()

        # Turn off echo
        curses.noecho()

        # Screen delay/block for 10th of a second
        if halfdelay:
            curses.halfdelay(self.halfdelay_screen_refresh)
        else:
            curses.halfdelay(255)

    def __check_terminal_size(self, scr) -> None:
        """
        Checking if current terminal size is sufficient, if it is not, display warning.

        Parameters:
            scr (obj): Handle for curses terminal screen handle
        Returns:
            None
        """
        # Getting the screen height and width
        term_height, term_width = scr.getmaxyx()

        # Check Height and width
        self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

        # Debug Terminal Size
        if logger.level == logging.DEBUG:
            scr.addstr(1, 1, f"[Terminal Size: W:{term_width}, H:{term_height}]", self.color['grey-light'])

        k = 0
        KEYS = utility.load_keys()
        while not self.terminal_size_good:
            if k in KEYS['QUIT']:
                self.exam_exit = True
                break

            # Re-evaluate the screen size
            term_height, term_width = scr.getmaxyx()
            self.terminal_size_good = term_height >= self.height_limit and term_width >= self.width_limit

            # if not self.exam_paused and not self.exam_quit:
            message_lines = [
                'Uh-Oh! Window size too small!', '', f'Current size is W:{term_width} by H:{term_height}',
                f'Size must be at least W:{self.width_limit} by H:{self.height_limit}', '',
                'Please resize window to continue', ''
                'To quit program press "Q" or "ESC"'
            ]
            # utility.draw_message_box(scr, message_lines)
            for y, line in enumerate(message_lines):
                scr.addstr(1 + y, 1, line, self.decor['bold'])

            scr.refresh()
            k = scr.getch()

    ###############################################################################################

    def __draw_selection_menu(self, scr, selections: list, start_y: int) -> None:
        """
        Draw a Selection menu at the bottom of the screen with a specified options

        Parameters:
            scr (obj)         : Handle for curses terminal screen handle
            selections (list) : Menu selection for each list item
            start_y (int)     : Line/row number at which selection menu starts
        Returns:
            None
        """
        # Getting the terminal size
        _, term_width = scr.getmaxyx()

        # Check if within boundaries of selection indexes
        self.selection_index = max(self.selection_index, 0)
        self.selection_index = min(self.selection_index, len(selections) - 1)

        # Get the x position of selection indicator
        longest_selection_text = len(max(selections, key=len))
        x_begin = term_width // 2 - longest_selection_text // 2 - 3
        x_end = term_width // 2 + longest_selection_text // 2 + 2

        y = 4

        for s, selection in enumerate(selections):
            if s == self.selection_index:
                # Color for highlighted selection text
                color = self.color['default'] | self.decor['bold']
                scr.addstr(y + s + 1 + start_y, x_begin, '|', color)
                scr.addstr(y + s + 1 + start_y, x_end, '|', color)
            else:
                color = self.color['grey-light']
            scr.addstr(y + s + 1 + start_y, term_width // 2 - len(selection) // 2, selection, color)

    def __draw_message_box(self, scr, message_lines: list) -> None:
        """
        Draw a message box in the middle of the terminal screen

        Parameters:
            scr (obj)            : Handle for curses terminal screen handle
            message_lines (list) : Lines of text in each list item
        Returns:
            None
        """
        term_height, term_width = scr.getmaxyx()

        # Getting the message box size and position and creating the message box
        height, width, y, x = utility.get_message_box_size(term_height, term_width, message_lines)
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

    ###############################################################################################

    def draw_menu(self, scr) -> Tuple[str, bool]:
        """
        Draw a the main menu on the screen

        Parameters:
            scr (obj)         : Handle for curses terminal screen handle
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr, halfdelay=False)
        KEYS = utility.load_keys()

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
                    # Start the Exam  # TODO: Prompt or countdown?
                    return 'begin', True
                elif self.selection_index == 1:
                    # Quit Program
                    if not self.is_exam_time_out:
                        self.exam_quit += 1

            elif k in KEYS['RESUME']:
                self.exam_quit = 0

            elif k in KEYS['QUIT']:
                if not self.is_exam_time_out:
                    self.exam_quit += 1

            ########################################################################################

            term_height, term_width = scr.getmaxyx()

            ########################################################################################

            # Check terminal size
            self.__check_terminal_size(scr)

            # Drawing the screen border
            utility.draw_screen_border(scr, self.color['grey-dark'])

            # Show software name/title
            scr.addstr(term_height - 2, 2, utility.load_software_name_version(), self.color['grey-dark'])

            ########################################################################################

            wrapper_menu_item = textwrap.TextWrapper(width=term_width - 25)

            start_y = 2
            start_x = [5, 22]

            line = f"{self.exam_contents['exam']['exam_title']}"
            scr.addstr(start_y, utility.center_x(term_width, line), line, self.decor['bold'])
            start_y += 1

            line = f"{self.exam_contents['exam']['exam_author']}"
            scr.addstr(start_y, utility.center_x(term_width, line), line, self.color['grey-light'])
            start_y += 1

            line = f"{self.exam_contents['exam']['exam_edit_date']}"
            scr.addstr(start_y, utility.center_x(term_width, line), line, self.color['grey-light'])
            start_y += 3

            lines = ["Description:", f"{self.exam_contents['exam']['exam_description']}"]
            menu_item_wrap = ' '
            for x, line_text in zip(start_x, lines):
                menu_item_wrap = wrapper_menu_item.wrap(text=line_text)
                for l, line in enumerate(menu_item_wrap):
                    scr.addstr(start_y + l - 1, x, line, self.color['default'])
            start_y += len(menu_item_wrap)

            lines = ["Exam Type:", self.exam_contents['exam']['exam_type']]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            lines = ["Questions:", f"{self.exam_contents['exam']['exam_questions_count']}"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            lines = [
                "Allowed Time:",
                f"{self.exam_contents['exam']['exam_allowed_time']} {self.exam_contents['exam']['exam_allowed_time_units']}"
            ]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            lines = ["Passing Score:", f"{self.exam_contents['exam']['exam_passing_score']} %"]
            for x, line in zip(start_x, lines):
                scr.addstr(start_y, x, line, self.color['default'])
            start_y += 2

            ########################################################################################

            selections = ["Begin Exam", "Quit"]
            utility.draw_horizontal_seperator(scr, term_height - len(selections) - 4, self.color['grey-dark'])
            start_y = term_height - len(selections) - 7
            self.__draw_selection_menu(scr, selections, start_y)

            ########################################################################################

            # Refresh the screen
            scr.refresh()

            ########################################################################################

            # Exam quit message box
            if self.exam_quit:
                curses.halfdelay(255)
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To return press "R"']
                self.__draw_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.exam_quit > 1:
                    return 'quit', True
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exist software
            if self.exam_exit:
                sys.exit(0)

            ########################################################################################

            # Get User input
            k = scr.getch()

    def show_menu(self) -> Tuple[str, bool]:
        """
        Curses wrapper function for drawing main menu on screen

        Parameters:
            None
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        return curses.wrapper(self.draw_menu)

    ###############################################################################################

    def __exam_timer_thread(self) -> None:
        """
        Exam timer that keeps track of elapsed exam time and exam paused time.
        Interactions to the main thread are via object properties.

        Parameters:
            None
        Returns:
            None
        """
        logger.debug('Starting exam timer thread ...')
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
        logger.debug('Exam timer thread ended')

    def draw_question(self, scr, question: dict) -> Tuple[str, bool]:
        """
        Draw a the current quesition on the screen

        Parameters:
            question (dict) : The current question information being presented
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr, halfdelay=True)
        KEYS = utility.load_keys()

        # Layout variables
        start_y = 3
        question_x = 4
        selection_x = 6

        # Selection / Answer Variables
        self.selection_index = 0
        question['answered_indexes'] = []
        question['answered_correct_bool'] = [False] * len(question['question_answer_bool'])

        # Loading question specific allowed time
        question_timer = True
        if 'question_allowed_time' in question.keys():
            if not isinstance(question['question_allowed_time'], int) or question['question_allowed_time'] < 1:
                logger.debug('Question allowed time not specified as integer or less than one second')
                question_timer = False
        else:
            logger.debug('Question allowed time not listed')
            question_timer = False

        # Start the question timer
        question_start_time = time()
        question_elapsed_time = 0

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
                    return 'quit', False

                elif not self.exam_paused:
                    correct_all = False
                    answer = ''
                    # Store or remove selection index
                    if self.selection_index not in question['answered_indexes']:
                        question['answered_indexes'].append(self.selection_index)
                    else:
                        index_to_remove = question['answered_indexes'].index(self.selection_index)
                        question['answered_indexes'].pop(index_to_remove)
                    logger.debug(f"Selected selection indexes: {question['answered_indexes']}")

                    # Determine correct or not correct
                    question['answered_correct_bool'][self.selection_index] = question['question_answer_bool'][
                        self.selection_index] != question['answered_correct_bool'][self.selection_index]
                    correct_all = question['question_answer_bool'] == question['answered_correct_bool']

                    answer = question['selection'][self.selection_index]

                    # Return the entered selections if all selections have been made
                    if len(question['answered_indexes']) >= question['question_min_selection_count']:
                        logging.debug('- Selection entered -')
                        return answer, correct_all

            elif k in KEYS['PAUSE']:
                self.exam_paused = True
                self.exam_paused_count += 1

            elif k in KEYS['RESUME']:
                self.exam_paused = False
                self.exam_quit = 0

            elif k in KEYS['QUIT']:
                if not self.is_exam_time_out:
                    self.exam_quit += 1

            ########################################################################################

            # Check terminal size
            self.__check_terminal_size(scr)

            # Drawing the screen border
            utility.draw_screen_border(scr, self.color['grey-dark'])

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
            l = 0
            for l, line in enumerate(question_wrap):
                scr.addstr(start_y + l - 1, question_x, line, self.color['default'] | self.decor['bold'])

            # Message of number of selections needed for current question
            message = []
            if question['question_multiselect']:
                message.append(f"Multiple Answers, Pick {question['question_min_selection_count']}")

            # Message of allowed time for current question
            if question_timer:
                message.append(f"Allowed Time: {question['question_allowed_time']:3.1f} seconds")

            # Construct the question message
            if question['question_multiselect'] or question_timer:
                color = self.color['grey-light']
                scr.addstr(start_y + l, question_x, "(" + ", ".join(message) + ")", color)
                line_offset = 1
            else:
                line_offset = 0

            utility.draw_horizontal_seperator(scr, len(question_wrap) + 3 + line_offset, self.color['grey-dark'])

            # Set the offset to the next line
            selection_offset = len(question_wrap) + 3 + line_offset

            # Wrap and show selection
            for s, selection in enumerate(question['selection']):

                selection_wrap = wrapper_selection.wrap(text=selection)
                for l, line in enumerate(selection_wrap):
                    # Style selection and draw selector
                    if s == self.selection_index:
                        color = self.color['default'] | self.decor['bold']
                        # Draw the selection indicator
                        scr.addstr(start_y + selection_offset + l - 1, selection_x - 2, self.selection_indicator,
                                   self.color['default'] | self.decor['bold'])
                    else:
                        color = self.color['grey-light']

                    # Style already selected indexes (for multi-select)
                    if question['question_multiselect']:
                        if s in question['answered_indexes']:
                            color = self.color['black-white']

                    scr.addstr(start_y + selection_offset + l - 1, selection_x + 2, line, color)

                # Set the offset to the next line
                selection_offset += len(selection_wrap) + 1

            ########################################################################################

            # Getting the screen height and width
            term_height, term_width = scr.getmaxyx()

            if question_timer:
                # Calculate current question time, and determine if timeout
                question_elapsed_time = time() - question_start_time
                if question_elapsed_time > question['question_allowed_time']:
                    logging.debug('Question timout')

                    # Determine correct or not correct at timeout
                    question['answered_correct_bool'][self.selection_index] = question['question_answer_bool'][
                        self.selection_index] != question['answered_correct_bool'][self.selection_index]
                    correct_all = question['question_answer_bool'] == question['answered_correct_bool']

                    question['answered_timeout'] = True
                    return 'timout', correct_all

                # Progress - Question Time
                elapsed_dec = question_elapsed_time / question['question_allowed_time']
                color = self.color['yellow']
                if elapsed_dec > 0.85 and elapsed_dec <= 0.92:
                    color = self.color['orange']
                if elapsed_dec > 0.92:
                    color = self.color['red'] | self.decor['bold']
                progress_bar = utility.get_progress_bar(exam_progress=elapsed_dec,
                                                        bar_char_width=term_width - 24,
                                                        bar_char_full="*")
                scr.addstr(
                    term_height - 4, 3,
                    f"[ {question_elapsed_time:3.1f}s / {question['question_allowed_time']:3.1f}s ][{progress_bar}]",
                    color)

            # Progress - Questions answered
            progress_bar = utility.get_progress_bar(exam_progress=self.questions_progress,
                                                    bar_char_width=term_width - 23)
            scr.addstr(term_height - 3, 3,
                       f"[ {self.questions_complete + 1:3.0f}  / {self.questions_total:3.0f}   ][{progress_bar}]",
                       self.color['default'])

            # Progress - Elapsed Exam Time
            elapsed_dec = self.exam_elapsed_time / self.exam_contents['exam']['exam_allowed_time']
            color = self.color['default']
            if elapsed_dec > 0.85 and elapsed_dec <= 0.92:
                color = self.color['orange']
            if elapsed_dec > 0.92:
                color = self.color['red'] | self.decor['bold']
            progress_bar = utility.get_progress_bar(exam_progress=elapsed_dec, bar_char_width=term_width - 23)
            scr.addstr(
                term_height - 2, 3,
                f"[ {self.exam_elapsed_time:3.0f}s / {self.exam_contents['exam']['exam_allowed_time']:3.0f}s  ][{progress_bar}]",
                color)

            ########################################################################################

            # Refresh the main screen layout
            scr.refresh()

            ########################################################################################

            # Exam pause message box
            if self.exam_paused and not self.exam_quit:
                message_lines = ['Exam was paused', 'To resume exam press "R"']
                self.__draw_message_box(scr, message_lines)

            # Exam quit message box
            if self.exam_quit:
                curses.halfdelay(255)
                self.exam_paused = True
                message_lines = [
                    'Are you sure you want to quit and evalute exam?', 'To quit and evaluate press "Q"',
                    'To resume exam press "R"'
                ]
                self.__draw_message_box(scr, message_lines)
                if self.exam_quit > 1:
                    # Quit Message confirmed (pressed twice)
                    return 'quit', False
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exist software
            if self.exam_exit:
                sys.exit(0)

            # Exam timed out message box
            if self.is_exam_time_out:
                message_lines = ['Exam time has expired', 'Press "ENTER" to evalute exam']
                self.__draw_message_box(scr, message_lines)

            ########################################################################################

            # Get User input
            k = scr.getch()

    def show_question(self, question: dict) -> Tuple[str, bool]:
        """
        Curses wrapper function for drawing single question on screen

        Parameters:
            question (dict) : The current question information being presented
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        return curses.wrapper(self.draw_question, question)

    ###############################################################################################

    def __evaluate_exam(self) -> None:
        """
        Evaluate the exam results

        Parameters:
            None
        Returns:
            None
        """
        logger.debug('Evaluating exam results ...')
        questions_count = len(self.exam_contents['questions'])

        # Get the score
        self.exam_contents['exam']['evaluation_percent'] = (self.questions_correct / questions_count) * 100

        # Get the score label/text
        if self.exam_contents['exam']['evaluation_percent'] >= self.exam_contents['exam']['exam_passing_score']:
            self.exam_contents['exam']['evaluation_label'] = "PASSED"
            self.exam_contents['exam']['evaluation_bool'] = True
        else:
            self.exam_contents['exam']['evaluation_label'] = "FAILED"
            self.exam_contents['exam']['evaluation_bool'] = False

    def __assemble_exam_results(self) -> dict:
        """
        Evaluate the exam results for presentation

        Parameters:
            None
        Returns:
            results (dict) : Combined and formatted exam results for presentation
        """
        results = {}
        index = 0

        results[index] = {
            "label": "Exam Title:",
            "text": self.exam_contents['exam']['exam_title'],  # TODO: Wrap or truncate
            "color": "default",
            "decor": "bold",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label": "Result:",
            "text": self.exam_contents['exam']['evaluation_label'],
            "color": "blue",
            "decor": "bold",
            "font_width": '',
            "skip_lines": 2
        }
        index += 1

        results[index] = {
            "label":
                "Correct:",
            "text":
                f"{self.exam_contents['exam']['evaluation_percent']:3.1f}% ({self.questions_correct} of {self.exam_contents['exam']['exam_questions_count']}) (Needed: {self.exam_contents['exam']['exam_passing_score']}%)",
            "color":
                "default",
            "decor":
                "normal",
            "font_width":
                '',
            "skip_lines":
                1
        }
        index += 1

        results[index] = {
            "label":
                "Questions Answered:",
            "text":
                f"{self.exam_contents['exam']['exam_questions_answered']} of {self.exam_contents['exam']['exam_questions_count']}",
            "color":
                "default",
            "decor":
                "normal",
            "font_width":
                '',
            "skip_lines":
                1
        }
        index += 1

        results[index] = {
            "label": "Exam Complete Time:",
            "text": f"{strftime('%H:%M:%S', gmtime(self.exam_elapsed_time))}",
            "color": "default",
            "decor": "normal",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label":
                "Exam Time Range:",
            "text":
                f"{self.exam_contents['exam']['exam_begin_datestring']} -> {self.exam_contents['exam']['exam_end_datestring']}",
            "color":
                "default",
            "decor":
                "normal",
            "font_width":
                '',
            "skip_lines":
                2
        }
        index += 1

        results[index] = {
            "label": "Number of Times Paused:",
            "text": str(self.exam_paused_count),
            "color": "default",
            "decor": "normal",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label": "Elapsed Paused Time:",
            "text": f"{strftime('%H:%M:%S', gmtime(self.exam_paused_elapsed_time))}",
            "color": "default",
            "decor": "normal",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        width = 33
        answer_distribution = ['.'] * width
        for question in self.exam_contents['questions']:
            if question['answered']:
                answer_distribution[int((question['answered_exam_time'] / self.exam_elapsed_time) * width) - 1] = "x"
        results[index] = {
            "label": "Answers Over Exam Time:",
            "text": f"[ 0.0s ]{''.join(answer_distribution)}[ {self.exam_elapsed_time:.1f}s ]",
            "color": "default",
            "decor": "normal",
            "font_width": 'fixed',
            "skip_lines": 1
        }
        index += 1

        answer_times = []
        for question in self.exam_contents['questions']:
            if question['answered']:
                answer_times.append(question['answered_question_time'])
        if answer_times:
            end_time = max(answer_times) * 1.25
        else:
            end_time = 1
        width = 33
        answer_distribution = ['.'] * width
        for answer_time in answer_times:
            answer_distribution[int((answer_time / end_time) * width) - 1] = "x"
        results[index] = {
            "label": "Answer Times:",
            "text": f"[ 0.0s ]{''.join(answer_distribution)}[ {end_time:.1f}s ]",
            "color": "default",
            "decor": "normal",
            "font_width": 'fixed',
            "skip_lines": 1
        }
        index += 1

        if len(answer_times) > 1:
            times_mean = mean(answer_times)
            times_std = stdev(answer_times)
            times_median = median(answer_times)

        else:
            times_mean = 0
            times_std = 0
            times_median = 0

        results[index] = {
            "label": "Average Time Per Answer:",
            "text": f"{times_mean:.1f} +/- {times_std:.2f} seconds",
            "color": "default",
            "decor": "normal",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        results[index] = {
            "label": "Median Time Per Answer:",
            "text": f"{times_median:.1f} seconds",
            "color": "default",
            "decor": "normal",
            "font_width": '',
            "skip_lines": 1
        }
        index += 1

        return results

    def draw_result(self, scr) -> Tuple[str, bool]:
        """
        Draw a results on the screen

        Parameters:
            None
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        # Setting up basic stuff for curses and load keys
        self.__basic_screen_setup(scr, halfdelay=False)
        KEYS = utility.load_keys()

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
                if not self.exam_quit:
                    self.selection_index += 1

            elif k in KEYS['UP'] or k in KEYS['LEFT']:
                if not self.exam_quit:
                    self.selection_index -= 1

            elif k in KEYS['ENTER']:
                if self.selection_index == 0:
                    # Save result PDF
                    return 'save', True
                elif self.selection_index == 1:
                    # Return to main menu
                    return 'menu', True
                elif self.selection_index == 2:
                    # Quit
                    self.exam_quit += 1

            elif k in KEYS['RESUME']:
                self.exam_quit = 0

            elif k in KEYS['QUIT']:
                self.exam_quit += 1

            ########################################################################################

            term_height, term_width = scr.getmaxyx()

            ########################################################################################

            # Check terminal size
            self.__check_terminal_size(scr)

            # Drawing the screen border
            utility.draw_screen_border(scr, self.color['grey-dark'])

            # Show software name/title
            scr.addstr(term_height - 2, 2, utility.load_software_name_version(), self.color['grey-dark'])

            ########################################################################################

            start_y = 2

            # Heading
            line = f"Exam Result Summary"
            scr.addstr(start_y, utility.center_x(term_width, line), line, self.decor['bold'])
            start_y += 2

            utility.draw_horizontal_seperator(scr, start_y, self.color['grey-dark'])
            start_y += 2

            # Draw items
            start_x = [4, 30]
            results = self.__assemble_exam_results()
            for _, item in results.items():
                scr.addstr(start_y, start_x[0], item['label'], self.color['default'])
                scr.addstr(start_y, start_x[1], utility.truncate_text(item['text'], term_width - 32),
                           self.color[item['color']] | self.decor[item['decor']])
                start_y += item['skip_lines']

            ########################################################################################

            selections = ["Save Result PDF and Quit", "Main Menu", "Quit"]  # TODO: "Review Question"
            utility.draw_horizontal_seperator(scr, term_height - len(selections) - 4, self.color['grey-dark'])
            start_y = term_height - len(selections) - 7
            self.__draw_selection_menu(scr, selections, start_y)

            ########################################################################################

            # Refresh the screen
            scr.refresh()

            ########################################################################################

            # Exam quit message box
            if self.exam_quit:
                curses.halfdelay(255)
                message_lines = ['Are you sure you want to quit?', 'To quit press "Q"', 'To return press "R"']
                self.__draw_message_box(scr, message_lines)
                # Quit Message confirmed (pressed twice)
                if self.exam_quit > 1:
                    return 'quit', True
            else:
                curses.halfdelay(self.halfdelay_screen_refresh)

            # Straight exist software
            if self.exam_exit:
                sys.exit(0)

            ########################################################################################

            # Get User input
            k = scr.getch()

    def show_result(self) -> Tuple[str, bool]:
        """
        Curses wrapper function for drawing the results on screen

        Parameters:
            None
        Returns:
            menu option (str)  : Selection menu option user selected (ie. quit)
            successfull (bool) : True if no error, else False
        """
        return curses.wrapper(self.draw_result)

    def export_results_to_pdf(self) -> bool:
        """
        Export all results to a PDF document.

        Parameters:
            None
        Returns:
            success (bool) : True if successfull, else False
        """
        page_width = 210
        page_height = 297

        page_left_margin = 10
        page_right_margin = 10
        # page_top_margin = 10
        page_bottom_margin = 20

        page_x_area = page_width - page_left_margin - page_right_margin
        # page_y_area = page_height - page_top_margin - page_bottom_margin

        # Setup Page
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_author("Author Test Terminal")
        pdf.set_creator("Creator Test Terminal")
        pdf.set_subject("Exam Results")
        pdf.add_page(orientation='P', format='A4', same=False)
        pdf.set_left_margin(margin=10)
        pdf.set_right_margin(margin=10)
        pdf.set_top_margin(margin=10)
        pdf.set_font('Helvetica', 'B', 18)  # Italics I, underline U
        # pdf.alias_nb_pages()

        # Draw border
        pdf.line(10, 10, 200, 10)
        pdf.line(10, 277, 200, 277)
        pdf.line(10, 10, 10, 277)
        pdf.line(200, 10, 200, 277)

        # Set the color depending on exam result label
        if self.exam_contents['exam']['evaluation_bool']:
            pdf.set_fill_color(r=220, g=255, b=220)
        else:
            pdf.set_fill_color(r=255, g=220, b=220)

        # Add Title
        pdf.set_text_color(*[0, 0, 0])
        pdf.cell(w=page_x_area, h=20, txt='Exam Results', border=1, align='C', fill=1)

        # Add result label
        pdf.set_font('Helvetica', '', 24)
        pdf.set_xy(x=page_width - page_right_margin - 70, y=page_height - page_bottom_margin - 40)
        pdf.cell(w=60, h=30, txt=self.exam_contents['exam']['evaluation_label'], border=1, align='C', fill=1)

        # Add Content
        results = self.__assemble_exam_results()
        pdf.set_text_color(*[0, 0, 0])
        start_x = [20, 77]
        start_y = 40
        line_height = 8
        for _, item in results.items():
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_xy(x=start_x[0], y=start_y)
            pdf.cell(w=60, h=line_height, txt=item['label'], border=0, align='L')

            if item['font_width'] == 'fixed':
                pdf.set_font('Courier', '', 11)
            else:
                pdf.set_font('Helvetica', '', 11)
            pdf.set_xy(x=start_x[1], y=start_y)
            pdf.cell(w=60,
                     h=line_height,
                     txt=utility.truncate_text(item['text'], self.width_limit - 25),
                     border=0,
                     align='L')

            start_y += item['skip_lines'] * 8

        # Add divider lines
        # pdf.line(page_width // 4, 60, 3*page_width // 4, 60)
        # pdf.line(page_width // 4, 100, 3*page_width // 4, 100)

        # Add the software watermark thingy
        pdf.set_text_color(*[100, 100, 100])
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_xy(x=page_left_margin + 3, y=page_height - page_bottom_margin - 8)
        pdf.cell(w=0, h=5, txt=f"Created with {utility.load_software_name_version()}", border=0, align='L')

        # Export the pdf to file
        datetime_text = datetime.fromtimestamp(
            self.exam_contents['exam']['exam_end_timestamp']).strftime("[%m-%d][%H-%M]")
        pdf_filepath = os.path.abspath(os.path.join('.', f'{datetime_text}_Exam_Result_Summary.pdf'))
        try:
            pdf.output(name=pdf_filepath, dest='F')
            logger.debug(f'Successfully saved exam results PDF: {pdf_filepath}')
        except Exception as e:
            logger.error(f'Failed to save exam results PDF document to "{pdf_filepath}". Exception: {e}')
            return False

        # Close
        pdf.close()

        return True

    ###############################################################################################

    def begin_exam(self) -> None:
        """
        Beginning of an exam. Looping through all specified questions

        Parameters:
            None
        Returns:
            None
        """
        logger.debug('Beginning Exam ...')
        self.exam_begin_time = time()

        # Start the independent timer thread for entire exam
        self.is_timer_timing = True
        exam_timer_thread = threading.Thread(target=self.__exam_timer_thread, args=())
        exam_timer_thread.daemon = True
        exam_timer_thread.start()

        # Looping over all listed questions
        for q, question in enumerate(self.exam_contents['questions']):
            logging.debug(f'Showing question number {q + 1}')

            # Start timer for current question
            question_elapsed_time = time()
            self.exam_contents['questions'][q]['question_presented_timestamp'] = question_elapsed_time

            # Show the question
            answer, correct = self.show_question(question)

            # Exam quit
            if answer == 'quit':
                break

            # Log answer metadata
            self.exam_contents['questions'][q]['answered'] = True
            self.exam_contents['questions'][q]['answered_timestamp'] = time()
            self.exam_contents['questions'][q]['answered_exam_time'] = self.exam_elapsed_time
            self.exam_contents['questions'][q]['answered_question_time'] = time() - question_elapsed_time
            self.exam_contents['questions'][q]['answered_correctly'] = correct

            # Increment completed question and correct or wrong answer
            self.questions_complete += 1
            if correct:
                self.questions_correct += 1
            else:
                self.questions_wrong += 1

            # Calculate Progress
            self.questions_progress = (self.questions_complete / self.questions_total)

        logger.debug('Exam completed or stopped')

        # Log exam attributes
        self.exam_contents['exam']['exam_begin_timestamp'] = self.exam_begin_time
        self.exam_contents['exam']['exam_end_timestamp'] = time()
        self.exam_contents['exam']['exam_begin_datestring'] = datetime.fromtimestamp(
            self.exam_contents['exam']['exam_begin_timestamp']).strftime("%m/%d/%Y, %H:%M:%S")
        self.exam_contents['exam']['exam_end_datestring'] = datetime.fromtimestamp(
            self.exam_contents['exam']['exam_end_timestamp']).strftime("%m/%d/%Y, %H:%M:%S")

        self.exam_contents['exam']['exam_questions_complete'] = self.questions_complete
        self.exam_contents['exam']['exam_questions_correct'] = self.questions_correct
        self.exam_contents['exam']['exam_questions_wrong'] = self.questions_wrong

        # Count exam question answered
        answered = 0
        for question in self.exam_contents['questions']:
            if question['answered']:
                answered += 1
        self.exam_contents['exam']['exam_questions_answered'] = answered

        # Stop independent exam timer
        self.is_timer_timing = False
        exam_timer_thread.join()

        # Evaluate the exam
        self.__evaluate_exam()

        if logger.level == logging.DEBUG:
            from pprint import pprint
            pprint(self.exam_contents)
