#!/usr/bin/env python3

import logging
import os
import sysconfig
import sys
from urllib.parse import urlparse

import click

from exam_terminal import exam_terminal, utility

# Creating a message logger, all dependent scripts will inhearent this logger
logging.basicConfig(format='[%(asctime)s][%(levelname)-8s] [%(filename)-30s:%(lineno)4s] %(message)s', datefmt='%m/%d-%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # <--- Manually change debug level here (DEBUG, INFO, ERROR, etc)
if logger.level == logging.DEBUG:
    logger.addHandler(logging.FileHandler("exam-terminal.log"))


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('-s', '--sample', is_flag=True, default=False, type=bool, help='Set this flag to run a sample exam, just to check things out')
@click.option('-e', '--examfile', required=False, default='', type=str, help='Local path or remote URL to the exam YAML file to be loaded')
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
            exam-terminal -e https://raw.githubusercontent.com/ismet55555/exam-terminal/master/exam_terminal/exams/sample_exam.yml

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
    exam_file_location = ''
    exam_file_contents = {}
    if sample and not examfile:
        # If local does not exist, try site-package
        exam_file_location = os.path.abspath(os.path.join("exam_terminal", "exams", "sample_exam.yml"))
        if not os.path.exists(exam_file_location):
            logger.debug(f'Failed to find {exam_file_location}, trying python site-package directory ...')
            site_package_dir = sysconfig.get_paths()["purelib"]
            exam_file_location = os.path.abspath(os.path.join(site_package_dir, "exam_terminal", "exams", "sample_exam.yml"))
        logger.debug(f'Using sample exam file: {exam_file_location}')

        # Load the file
        exam_file_contents = utility.load_examfile_contents_from_local_file(exam_file_location)

    # Specified exam file location
    if examfile:
        # Check if examfile is passed as local path or remote URL to be downloaded
        if bool(urlparse(examfile).scheme):
            # Loading file from remote URL
            exam_file_contents = utility.load_examfile_contents_from_url(examfile)
        else:
            # Loading local file
            logger.debug(f'Passed local exam file: {click.format_filename(examfile)}')
            exam_file_location = os.path.abspath(click.format_filename(examfile))
            logger.debug(f'Interpreted local exam file path: {exam_file_location}')

            # Check if examfile exists locally
            if not os.path.exists(exam_file_location):
                ctx = click.get_current_context()
                click.echo(click.style("Uh-Oh! Something's wrong here ...", fg='bright_red', bold=True))
                ctx.fail(click.style(f"User Input Error: The exam file which you specified does not exist: {exam_file_location}", fg='bright_red', bold=True))

            # Load the file
            exam_file_contents = utility.load_examfile_contents_from_local_file(exam_file_location)

    # Run exam-terminal
    exitcode = 0
    if exam_file_contents:
        exitcode = exam_terminal.exam_terminal(exam_file_contents)
    else:
        ctx = click.get_current_context()
        ctx.fail(click.style(f"Failed to load the specified file '{examfile}'. Check file location or format.", fg='bright_red', bold=True))

    if not exitcode:
        click.echo(click.style("Done", fg='bright_green', bold=True))

    sys.exit(exitcode)


if __name__ == "__main__":
    """
    Main entry point to the entire program.
    This file and this function will be called when running the program.

    Parameters: None
    Returns: None
    """
    main()
