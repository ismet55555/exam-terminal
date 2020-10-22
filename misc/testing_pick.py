from pick import pick
import sys
import os
import yaml
from pprint import pprint
from loguru import logger

from ExamTerminal import ExamTerminal

os.system('cls' if os.name == 'nt' else 'clear')

et = ExamTerminal()
et.load_parse_examfile("sample_questions.yml")
et.begin_exam()
et.get_exam_info()