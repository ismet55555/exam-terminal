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
@click.option('-s', '--sample', is_flag=True, default=False, type=bool, help='Set this flag to a sample exam, just to check things out')
@click.option('-e', '--examfile', required=False, default='', type=str, help='Relative or absolute path to the exam file to be loaded')
def main(sample, examfile) -> None:
    """
        \b
                                       _                      _             _ 
                                      | |                    (_)           | |
         _____  ____ _ _ __ ___ ______| |_ ___ _ __ _ __ ___  _ _ __   __ _| |
        / _ \ \/ / _` | '_ ` _ \______| __/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
       |  __/>  < (_| | | | | | |     | ||  __/ |  | | | | | | | | | | (_| | |
        \___/_/\_\__,_|_| |_| |_|      \__\___|_|  |_| |_| |_|_|_| |_|\__,_|_|
                                                                        
        Use this little terminal program to perform a exam/quiz/test using a
        predefined YML (or YAML) file containing exam information.

        \b
        Example Usages:
            exam-terminal --sample
            exam-terminal -e MyExam.yml
            exam-terminal -examfile ~/Documents/Exams/SomeExam.yaml
            exam-terminal -e "/home/you/review.yml"

        For even more help visit:
        https://github.com/ismet55555/exam-terminal
    """
    logger.debug(f'--sample = {sample}')
    logger.debug(f'--examfile = {examfile}')

    # Check if any options have been passed
    if not sample and not examfile:
        ctx = click.get_current_context()
        click.echo(click.style("Uh-Oh! Something's wrong here ...", fg='bright_red', bold=True))
        ctx.fail(click.style("User Input Error: No exam-terminal options were specified. Please specify any option.", fg='bright_red', bold=True))

    # Sample examfile
    exam_filepath = ''
    if sample and not examfile:
        exam_filepath = os.path.abspath(click.format_filename("exams/sample_exam.yml"))
        logger.debug(f'Using sample exam file: {exam_filepath}')

    # Specified examfile
    if examfile:
        logger.debug(f'Passed exam file: {click.format_filename(examfile)}')
        exam_filepath = os.path.abspath(click.format_filename(examfile))
        logger.debug(f'Interpreted exam file path: {exam_filepath}')

    # Check if examfile exists
    if not os.path.exists(exam_filepath):
        ctx = click.get_current_context()
        click.echo(click.style("Uh-Oh! Something's wrong here ...", fg='bright_red', bold=True))
        ctx.fail(click.style(f"User Input Error: The exam file which you specified does not exist: {exam_filepath}", fg='bright_red', bold=True))

    # Run exam-terminal
    exitcode = exam_terminal.exam_terminal(exam_filepath=exam_filepath)

    if not exitcode:
        click.echo(click.style("Done", fg='bright_green', bold=True))

    sys.exit(exitcode)


if __name__ == "__main__":
    """
    Main entry point to the entire program.
    This file and this function will be called when running the program

    Parameters: None
    Returns: None
    """
    main()
