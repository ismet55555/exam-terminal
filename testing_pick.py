from pick import pick
import sys
import os
import yaml
from pprint import pprint
from loguru import logger


# logger.add(sys.stderr, format="[{time}][{level}] {message}", filter="my_module", level="INFO")

os.system('cls' if os.name == 'nt' else 'clear')


class ExamTerminal:

    def __init__(self) -> None:
        # Constructor
        self.exam_filepath = ""
        self.exam_contents = {}
        self.indicator = " --> "
        logger.info('Exam object created')


    def load_examfile(self, filepath: str) -> bool:
        self.exam_filepath = filepath

        # Load the questions
        logger.info("Loading specified exam file: '{filepath}' ...")
        try:
            with open(filepath) as file:
                self.exam_contents = yaml.load(file, Loader=yaml.FullLoader)
        except Exception as e:
            logger.error(f"Failed to load specified exam file: '{filepath}'")


    def parse_examfile(self) -> bool:
        logger.info('Parsing the loaded exam information ...')

        # Loop through all the questions
        for question in self.exam_contents['questions']:
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


        return True


    def begin_exam(self) -> bool:
        # Loop through all the questions
        for question in self.exam_contents['questions']:
            if question['multiselect']:
                multiselect_prompt = f" [Select {sum(question['answer_bool'])} using the SPACEBAR]"
            else:
                multiselect_prompt = ""


            title = question['question'] + multiselect_prompt
            options = question['selection']
            user_selected = pick(options, 
                            title, 
                            multiselect=question['multiselect'], 
                            min_selection_count=question['min_selection_count'])


            # Ensure that the answer is in a list format
            if question['multiselect']:
                user_selected_formatted = user_selected
            else:
                user_selected_formatted = [user_selected]

            # Check the answer
            current_correct = 0
            for s in user_selected_formatted:
                if s[1] in question['answer_indexes']:
                    current_correct += 1

            # Check if user gave all correct selections
            if current_correct == sum(question['answer_bool']):
                print("CORRECT!")
            else:
                print("WRONG")

            input('\nPress any key to continue')


    def get_score(self) -> bool:
        pass


    def get_exam_info(self, pretty=True) -> dict:
        return self.exam_contents


et = ExamTerminal()
et.load_examfile("sample_questions.yml")
et.parse_examfile()
# pprint(et.get_exam_info())
et.begin_exam()

