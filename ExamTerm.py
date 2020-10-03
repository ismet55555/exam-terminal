
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

        self.indicator = "|"
        self.selection_index = 0

        # Loading exam contents
        self.exam_contents = self.load_parse_examfile(self.exam_filepath)

        self.questions_total = len(self.exam_contents['questions'])
        self.questions_complete = 0
        self.questions_current = 0
        self.exam_progress = 0

        self.questions_correct = 0
        self.questions_wrong = 0

        self.exam_begin_time = 0
        self.elapsed_time = 0

        self.exam_paused = False

        self.timer_timing = False

        logger.info('Exam object created')

    def load_parse_examfile(self, filepath: str) -> dict:
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

    def begin_exam(self):
        logger.info('Exam started')

        self.exam_begin_time = time()

        # Start the independent timer thread for entire exam
        self.timer_timing = True
        exam_timer_thread = threading.Thread(target=self.exam_timer_thread, args=())
        exam_timer_thread.daemon = True
        exam_timer_thread.start()

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
            self.exam_contents['questions'][q]['answered_exam_time'] = self.elapsed_time
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
            self.exam_progress = (self.questions_complete / self.questions_total)

        # Stop independent exam timer
        self.timer_timing = False
        exam_timer_thread.join()

        pprint(self.exam_contents)

    def show_question(self, question):
        return curses.wrapper(self.draw_question, question)

    def show_menu(self):
        return curses.wrapper(self.draw_menu)

    def exam_timer_thread(self):
        while self.timer_timing:
            if not self.exam_paused:
                self.elapsed_time = time() - self.exam_begin_time

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

    def draw_question(self, stdscr, question):
        # Predefine and pre-allocate variables
        k = 0

        # Hiding the cursor
        curses.curs_set(0)

        # Start colors in curses
        curses.start_color()

        # Define the colors to be used (foreground and background) (ie. curses.color_pair(1))
        #     curses.init_pair(color reference index, font color number, background color number)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, 248, curses.COLOR_BLACK)  # Grey

        # Turn off echo
        curses.noecho()

        # Non-blocking for user
        stdscr.nodelay(True)

        # Define keys
        KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
        KEYS_UP = (curses.KEY_UP, ord('k'))
        KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
        KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))
        KEYS_PAUSE = ord('p')
        KEYS_QUIT = ord('q')

        quesiton_x = 8
        selection_x = 10
        start_y = 5

        # Reset selection
        self.selection_index = 0

        # Main Loop
        while True:
            # Clearing the screen at each loop iteration before constructing the frame
            stdscr.clear()

            ########################################################################################

            # Getting the screen height and width
            term_height, term_width = stdscr.getmaxyx()

            # Check terminal size
            # TODO: Do something when terminal size is not right
            #       Pause and box?
            if term_width >= 80:
                whstr = "[Terminal Size: W:{}, H:{}]".format(term_width, term_height)
                stdscr.addstr(0, 0, whstr, curses.color_pair(1))
            else:
                stdscr.addstr(0, 0, "Terminal Must be wider than 80 characters!", curses.color_pair(1))

            stdscr.attron(curses.color_pair(6))
            stdscr.border(0)
            stdscr.attroff(curses.color_pair(6))
            
            ########################################################################################

            # Check user input and adjust the cursor movement
            if k in KEYS_DOWN:
                self.selection_index += 1

            elif k in KEYS_UP:
                self.selection_index -= 1

            elif k in KEYS_ENTER:
                index = self.selection_index
                correct = question['answer_bool'][self.selection_index]
                answer = question['selection'][self.selection_index]
                return index, answer, correct

            elif k == KEYS_PAUSE:
                stdscr.addstr(1, 0, "DEBUG PAUSE", curses.color_pair(1))

            elif k == KEYS_QUIT:
                break

                # POP UP CURSES BOX

            ########################################################################################

            # Check if within boundaries of selection indexes
            self.selection_index = max(self.selection_index, 0)
            self.selection_index = min(self.selection_index, len(question['selection']) - 1)

            ########################################################################################

            # Create text wrappers
            wrapper_question = textwrap.TextWrapper(width=60)
            wrapper_selection = textwrap.TextWrapper(width=40)

            # Wrap and show the question
            question_wrap = wrapper_question.wrap(text=question['question']) 
            for l, line in enumerate(question_wrap):
                stdscr.addstr(start_y + l - 1, quesiton_x, line)

            # Set the offset to the next line
            selection_offset = len(question_wrap) + 3

            # Wrap and show selection
            for s, selection in enumerate(question['selection']):

                if s == self.selection_index:
                    stdscr.attron(curses.color_pair(5))

                selection_wrap = wrapper_selection.wrap(text=selection)
                for l, line in enumerate(selection_wrap):
                    stdscr.addstr(start_y + selection_offset + l - 1, selection_x + 2, line)

                    # Draw selector
                    if s == self.selection_index:
                        # if l == 0:
                            # stdscr.addstr(start_y + selection_offset + l - 1, selection_x - 3, self.indicator)
                        stdscr.addstr(start_y + selection_offset + l - 1, selection_x - 2, self.indicator)

                stdscr.attroff(curses.color_pair(5))

                # Set the offset to the next line
                selection_offset += len(selection_wrap) + 1

            ########################################################################################

            # Progress bar and status - call method
            stdscr.attron(curses.color_pair(6))
            stdscr.addstr(term_height - 3, 3, f"[ {self.questions_complete:3.0f}  / {self.questions_total:3.0f}  ][{self.get_progress_bar(self.exam_progress, bar_char_width=term_width-23)}]")

            ########################################################################################

            # Elapsed Time
            stdscr.addstr(term_height - 2, 3, f"[ {self.elapsed_time:3.0f}s / {self.exam_total_time:3.0f}s ][{self.get_progress_bar(self.elapsed_time / 60, bar_char_width=term_width-23)}]")
            stdscr.attroff(curses.color_pair(6))

            ########################################################################################

            # Terminal Outline (Only for terminals larger than X, Y)
            # for i in range(2, term_width-1):
            #     stdscr.addstr(2, i, "-")
            #     stdscr.addstr(term_height - 2, i, "-")

            # for i in range(2, term_height - 1):
            #     stdscr.addstr(i, 1, "|") 
            #     stdscr.addstr(i, term_width - 1, "|")

            ########################################################################################

            # Refresh the screen
            stdscr.refresh()

            # Get User input
            k = stdscr.getch()

        return -1, 'quit', False



exam = Exam()
exam.begin_exam()


