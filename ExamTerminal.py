
from pick import pick
from pprint import pprint
from loguru import logger
import yaml


class ExamTerminal:

    def __init__(self) -> None:
        # Constructor
        self.exam_filepath = ""
        self.exam_contents = {}
        self.indicator = " --> "
        logger.info('Exam object created')


    def load_parse_examfile(self, filepath: str) -> bool:
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
                            indicator=self.indicator,
                            multiselect=question['multiselect'], 
                            min_selection_count=question['min_selection_count'])


            # Ensure that the answer is in a list format
            if question['multiselect']:
                # Multi-select question
                user_selected_formatted = user_selected
            else:
                # Single selection
                user_selected_formatted = [user_selected]

            # Check the answer for all selections
            current_correct = 0
            for s in user_selected_formatted:
                if s[1] in question['answer_indexes']:
                    current_correct += 1

            # Evaluate and store answer
            if current_correct == sum(question['answer_bool']):
                logger.info("Answer Correct")
                question['answer_correct'] = True
            else:
                logger.info("Answer Wrong")
                question['answer_correct'] = False

            # input('Press any key to continue')


    def get_score(self) -> bool:

        # Add a key
        self.exam_contents['evaluation']

        
        pass


    def get_exam_info(self, pretty=True) -> dict:
        pprint(self.exam_contents)
        return self.exam_contents