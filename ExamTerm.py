
import curses
from pprint import pprint
from time import sleep, time
from loguru import logger
import yaml
import threading


class Exam:
    def __init__(self) -> None:
        # Constructor
        self.exam_filepath = ""
        self.exam_contents = self.load_parse_examfile("sample_questions.yml")

        self.stdscr = None

        self.indicator = ">"
        self.selection_index = 0

        self.questions_total = len(self.exam_contents['questions'])
        self.questions_complete = 0
        self.questions_current = 0
        self.exam_progress = 0
        self.exam_progress_percent = 0

        self.questions_correct = 0
        self.questions_wrong = 0

        self.exam_begin_time = 0

        self.timer_timing = False
        
        logger.info('Exam object created')

    def load_parse_examfile(self, filepath: str) -> dict:
        self.exam_filepath = filepath

        # Load the examp file
        logger.info(f"Loading specified exam file: '{filepath}' ...")
        try:
            with open(filepath) as file:
                self.exam_contents = yaml.load(file, Loader=yaml.FullLoader)
        except Exception as e:
            logger.error(f"Failed to load specified exam file: '{filepath}'")
            return False

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

        pprint(self.exam_contents)

        # Get the total number of questions
        self.questions_total = len(self.exam_contents['questions'])

        return self.exam_contents

    def begin_exam(self):
        logger.info('Exam started')

        self.exam_begin_time = time()

        for question in self.exam_contents['questions']:
            index, answer, correct = exam.show_question(question)
            logger.info(answer)

            # Increment correct or wrong answer
            if correct:
                self.questions_correct += 1
            else:
                self.questions_wrong += 1

            # Increment questions compelted
            self.questions_complete += 1

            # Calculate Progress
            self.exam_progress_percent = (self.questions_complete / self.questions_total) * 100



    def show_question(self, question):
        return curses.wrapper(self.draw_question, question)

    def show_menu(self):
        return curses.wrapper(self.draw_menu)

    def exam_timer_thread(self):
        while self.timer_timing:
            elapsed_time = time() - self.exam_begin_time
            self.stdscr.addstr(22, 9, f"{elapsed_time:.2f}")
            self.stdscr.refresh()
            # logger.critical('YO')
            sleep(1.0)

    def draw_question(self, stdscr, question):

        self.stdscr = stdscr

        # Start the independent thread
        self.timer_timing = True
        exam_timer_thread = threading.Thread(target=self.exam_timer_thread, args=())
        exam_timer_thread.daemon = True
        exam_timer_thread.start()

        # Predefine and pre-allocate variables
        k = 0

        # Hiding the cursor
        curses.curs_set(0)

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Define keys
        KEYS_ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
        KEYS_UP = (curses.KEY_UP, ord('k'))
        KEYS_DOWN = (curses.KEY_DOWN, ord('j'))
        KEYS_SELECT = (curses.KEY_RIGHT, ord(' '))

        # Turn off echo
        curses.noecho()

        start_x = 9
        start_y = 10




        # Loop where k is the last character pressed
        while (k != ord('q')):
            ########################################################################################

            # Clearing the screen at each loop iteration
            stdscr.clear()



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
                self.timer_timing = False
                exam_timer_thread.join()
                
                return index, answer, correct

            # Check if within boundaries of selection indexes
            self.selection_index = max(self.selection_index, 0)
            self.selection_index = min(self.selection_index, len(question['selection']) - 1)

            ########################################################################################

            # Show the question
            stdscr.addstr(start_y - 3, start_x, question['question'])

            # List selections
            for i, selection in enumerate(question['selection']):
                stdscr.addstr(start_y + i, start_x, selection)

            # Draw selector
            stdscr.addstr(start_y + self.selection_index, start_x - 2, self.indicator)

            ########################################################################################

            # Progress bar and status - call method
            stdscr.addstr(20, start_x, f"{self.exam_progress_percent:.2f}")

            ########################################################################################

            # Elapsed TIme (count down) - call method
            # Also a progress bar
            # elapsed_time = time() - self.exam_begin_time
            # stdscr.addstr(22, start_x, f"{elapsed_time:.2f}")


            ########################################################################################


            # Refresh the screen
            stdscr.refresh()

            # Wait for next user input
            k = stdscr.getch()
            


exam = Exam()
exam.begin_exam()


