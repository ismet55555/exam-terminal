
#!/usr/bin/env python3

from ExamTerminal import ExamTerminal
import os
import logging

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def exam_terminal() -> int:
    """
    Beginning of program. Called from __main__.py

    Parameters: None
    Returns:
            exit code (int): Program exit code

    """

    logger.debug(f"Current directory: {os.getcwd()}")

    # TODO: Smarter menu navigation

    while True:
        # Create the exam object and loading the exam file
        exam = ExamTerminal(exam_filepath="exams/exam.yml")

        # Show the intro 
        main_menu_selection = exam.show_menu()

        if main_menu_selection[0] == 'begin':
            # Begin the exam
            exam.begin_exam()

            # Show exam results
            result_menu_selection = exam.show_result()

            # If selected export the results to pdf
            if result_menu_selection[0] == 'save':
                exam.export_results_to_pdf()
                break
            elif result_menu_selection[0] == 'menu':
                pass
            else:
                break
        else:
            break

    return 0
