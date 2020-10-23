#!/usr/bin/env python3

import logging
import os
import sys

import click

from exam_terminal import exam_terminal

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

@click.command(context_settings={"ignore_unknown_options": True})
@click.argument('examfile', nargs=1, type=click.Path(exists=True, allow_dash=True))
def main(examfile) -> None:
    """
        Use this program to perform a exam/quiz/test using a
        predefined YML (or YAML) file

        \b
        Example Usages:
            exam_terminal MyExam.yml
            exam_terminal ~/Documents/Exams/SomeExam.yaml
            exam_terminal "/home/you/review.yml

        EXAMFILE is the path and/or name to the exam file.
    """
    logger.debug(f'Passed exam file: {click.format_filename(examfile)}')

    exam_filepath = os.path.abspath(click.format_filename(examfile))
    logger.debug(f'Interpreted exam file path: {exam_filepath}')

    exitcode = exam_terminal.exam_terminal(exam_filepath=exam_filepath)
    sys.exit(exitcode)


if __name__ == "__main__":
    """
    Main entry point to the entire program.
    This file and this function will be called when running the program

    Parameters: None
    Returns: None
    """
    main()
