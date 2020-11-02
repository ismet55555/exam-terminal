# TODO

## General

  - README.md
    - Record terminalizer demo video
    - How to put together a exam file

## Code Structure

  - ...

## Main Menu

  - Add a About, Settings, Help, Options
  - Options menu
    - Immediate result feedback
    - Show Time
    - Show Progress
  - Save all variables to the exam_contents dict

## Exam Loading

  - Allowed time units
  - Enter exam taker name?
    - Add CLI option for exam taker's name
  - Simple database? or just a file?
  - Encrypt the exam file with a password so you can send it to someone?
  - SQLite database somewhere in AWS? Github?
  - Add few sample exams
    - Docker Certified Accosiate (DCA)
    - AWS Practitioner
    - Ansible RedHat Cert
    - Algebra / Calculus Math exams
    - Python Programming Fundementals
  - Better way to format and load exam
    - Markdown?
    - Both Yaml and markdown?

## Exam Formatting and Navigation

  - Go back and forth with questions
  - Have a answered/unanswered questions indicator

## Exam

  - Immediate question-by-question based feedback

## Pause/Resume Exam

  - Quitting exam with option to continue later -> create a temp .exam file
  - Auto save to protect against crashes
  - Auto Timeout on question taking too long (maybe X% of total test ...)

## Results

  - Give user option to save exam format
    - PDF
    - .json data
    - .yml data
    - Standard out as json data
    - Send via email

## Python Package Packaging

  - ...

## Testing and Continues Integration

  - Get `bumpversion` to work to automatically increase version for every push
  - Travis CI
    - OSX and Windows testing
      - Example: https://github.com/IntelRealSense/librealsense/blob/master/.travis.yml
      - Possibly need custom python setup
    - Figure out windows and osx tests jobs
    - Code linting and formatting check
    - Omit travis testing when changes to .md files were made
      - Maybe get that `scripts/preflight.sh` to work?
  - Add more tests somehow, not sure how to test curses apps

## Random

  - Fix Docstrings for new loading feature

# Bugs

  - Package PYPI version shield in README.md not updating
    - https://github.com/lemurheavy/coveralls-public/issues/971
