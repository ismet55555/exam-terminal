
#!/usr/bin/env python3

from ExamTerminal import ExamTerminal
import os
import logging

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def exam_terminal() -> int:
    """Code here"""

    logger.debug(f"Current directory: {os.getcwd()}")

    exam = ExamTerminal(exam_filepath="exams/exam.yml")
    menu_result = exam.show_menu()
    if menu_result:
        exam.begin_exam()

        exam.show_result()

        exam.export_results_to_pdf()

    return 0
