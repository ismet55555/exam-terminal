# TODO

## General

  - README.md
    - Record terminalizer demo video

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
  - Survey mode option?
  - Enter exam taker name?
    - Add CLI option for exam taker's name
  - Encrypt the exam file with a password so you can send it to someone?
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

  - Navigate back and forth with questions (skip questions)
  - Have a answered/unanswered questions indicator

## Exam

  - Immediate question-by-question based feedback
    - Show the right answer immediatelly when selected

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

  - ...

# Bugs

  - ...
