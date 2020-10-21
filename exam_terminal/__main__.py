#!/usr/bin/env python3

import sys

from exam_terminal import exam_terminal


def main():
    exitcode = exam_terminal()
    sys.exit(exitcode)


if __name__ == "__main__":
    """ 
    Main entry point to the entire program.
    This file and this function will be called when running the program
    """
    main()
