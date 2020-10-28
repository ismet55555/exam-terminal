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
- ...

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
  - `exams/sample_exam.yml` must be available at package install
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
- Give user option to save exam format
  - PDF
  - .json data
  - .yml data
  - Standard out as json data


## Python Package Packaging
- Include sample exams with https://packaging.python.org/guides/using-manifest-in/
  - package_data  or  data_files
- `bumpversion` with automatic bump at push


## Random
- Update version number within exam
  - Read from setup.py ?


# Bugs
- I'm sure there are some lurking in the dark ...
