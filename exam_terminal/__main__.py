#!/usr/bin/env python3

import sys

import click

from exam_terminal import exam_terminal

@click.command()
@click.option('--test', default='World', help="Testing some stuff")
def main(test) -> None:
    click.echo(test)
    return
    exitcode = exam_terminal.exam_terminal()
    sys.exit(exitcode)


if __name__ == "__main__":
    """
    Main entry point to the entire program.
    This file and this function will be called when running the program

    Parameters: None
    Returns: None
    """
    main()
