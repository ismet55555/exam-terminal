# TODO 

## General
- README.md
- Python DocStrings
- A few sample exams
  - DCA
  - AWS Practitioner
  - Ansible
- Simple database? or just a file?
- Animations on switch screen?  Side fille, bottom fill?
- Run out of a Docker image (make the Dockerfile)
- See example https://github.com/PyCQA/redbaron for flairs and tests

## Code Structure
- Break appart ExamTerminal.py to multiple files
  - utility.py ?

## Main Menu
- Add a About, Settings, Help Options (Horizontal? Two Lines?)
- Options menu
  - Immediate result feedback
  - Show Time
  - Show Progress
- Save all variables to the exam_contents dict


## Exam Loading
- Enter exam taker name?
- Add a sample sample_exam.yml, that is called with option --sample
- Add CLI option for exam taker's name
- Encrypt the exam file with a password so you can send it to someone?
- Better way to format and load exam
  - Markdown?
  - Both Yaml and markdown?


## Exam Formatting and Navigation
- Go back and forth with questions
- Have a answered/unanswered questions indicator 
- Set up where multiple choice selection yields something backce


## Pause/Resume Exam
- Quitting exam with option to continue later -> create a temp .exam file
- Auto save to protect against crashes
- Auto Timeout on question taking too long (maybe X% of total test ...)


## Results
- Ability to send exam results via email
  - PDF
  - .json data
  - .yml data


## Python Package Packaging
- At install, Print out a nice ASCII sign with scripts=['scripts/xmlproc_parse', 'scripts/xmlproc_val'] or in requirements():
- Include sample exams with https://packaging.python.org/guides/using-manifest-in/
  - package_data  or  data_files

## Testing and Continues Integration
- Get bumpversion to work to automatically increase version for every push
- Travis CI: Figure out windows and osx tests jobs
- Travis CI: Code linting and formatting check
- Travis CI: Omit travis testing when changes to .md files were made
- Add pep8, black, isort, tests


## Random
- ...


# Bugs
- I'm sure there are some lurking in the dark ...
