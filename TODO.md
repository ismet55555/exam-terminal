# TODO

## General

  - README.md
    - Record terminalizer demo video
  - Simple database? or just a file?
  - Run out of a Docker image (make the Dockerfile)

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

  - Enter exam taker name?
  - Add a sample sample_exam.yml, that is called with option --sample
    - `exams/sample_exam.yml` must be available at package install
  - Add CLI option for exam taker's name
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
  - Set up where multiple choice selection yields something backce

## Exam

  - Immediate question-by-question based feedback
  - Time constraint for each question

## Pause/Resume Exam

  - Quitting exam with option to continue later -> create a temp .exam file
  - Auto save to protect against crashes
  - Auto Timeout on question taking too long (maybe X% of total test ...)

## Results

  - Ability to send exam results via email
  - Give user option to save exam format
    - PDF
    - .json data
    - .yml data
    - Standard out as json data

## Python Package Packaging

  - `bumpversion` with automatic bump at push

## Testing and Continues Integration

  - Get bumpversion to work to automatically increase version for every push
  - Travis CI
    - OSX and Windows testing
      - Example: https://github.com/IntelRealSense/librealsense/blob/master/.travis.yml
      - Possibly need custom python setup
    - Figure out windows and osx tests jobs
    - Code linting and formatting check
    - Omit travis testing when changes to .md files were made
  - Add tests

## Random

  - ...

# Bugs

  - I'm sure there are some lurking in the dark ...
