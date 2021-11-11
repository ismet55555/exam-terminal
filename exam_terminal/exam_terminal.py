#!/usr/bin/env python3

import logging
import os

from . import ExamTerminal

logger = logging.getLogger()


def exam_terminal(exam_file_contents: dict) -> int:
    """
    Beginning of program. Called from __main__.py

    Parameters:
        exam_file_contents (dict): Pre-loaded exam contents
    Returns:
        exit code (int): Program exit code

    """
    current_working_dir = os.getcwd()
    logger.debug(f"Current directory: {current_working_dir}")

    # TODO: Smarter menu navigation

    # Number of attempts
    exam_attempt = 0

    while True:
        # Create the exam object and loading the exam file
        exam = ExamTerminal.ExamTerminal(exam_file_contents, exam_attempt)

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

        # Increment exam exam_attempt
        exam_attempt += 1

    return 0
