<p align="center"><img width="150" alt="portfolio_view" src="https://raw.githubusercontent.com/ismet55555/exam-terminal/master/misc/logo.png"></p>

<h1 align="center">exam-terminal</h1>

<!-- Licence Shield from https://shields.io/-->
<p align="center">

<a href="https://pypi.org/project/exam-terminal/">
  <img alt="PYPI Version" src="https://img.shields.io/pypi/v/exam-terminal?color=blue">
</a>

<a href="https://pypi.org/project/exam-terminal/">
  <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/exam-terminal">
</a>

<a href="https://pypi.org/project/exam-terminal/">
  <img alt="Packaging Format" src="https://img.shields.io/pypi/format/exam-terminal">
</a>

<a href="https://pypi.org/project/exam-terminal/">
  <img alt="PYPI Status" src="https://img.shields.io/pypi/status/exam-terminal">
</a>

<a href="https://github.com/ismet55555/exam-terminal/blob/master/LICENSE">
  <img alt="Licence" src="https://img.shields.io/github/license/ismet55555/exam-terminal">
</a>

<a href="https://travis-ci.com/github/ismet55555/exam-terminal">
  <img alt="Build Status" src="https://img.shields.io/travis/com/ismet55555/exam-terminal/master">
</a>

<a href="https://www.codacy.com/gh/ismet55555/exam-terminal/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ismet55555/exam-terminal&amp;utm_campaign=Badge_Grade">
  <img src="https://app.codacy.com/project/badge/Grade/dc108e18f27b4b86a9f6304745e6869c"/>
</a>
</p>


The `exam-terminal` is a terminal-based assessment tool. It can be used for making, taking, or delivering exams or quizzes.

<p align="center"><img width="725" alt="demo_gif" src="https://raw.githubusercontent.com/ismet55555/exam-terminal/master/misc/demo.gif"></p>

Exam description can be loaded form a local file or a remote URL link.

The exam results include your general exam score, some basic statistics, and the ability to export your results to a PDF document.

### Very Basically ...
  - Use `exam-terminal` to take or give exams in a terminal


<!-- ################################################ -->


# :eyeglasses: Overview

- [:eyeglasses: Overview](#eyeglasses-overview)
- [:fast_forward: Quick Start](#fast_forward-quick-start)
- [:thumbsup: Compatibility](#thumbsup-compatibility)
- [:rocket: Installation](#rocket-installation)
  - [Install It From PYPI (pre-build)](#install-it-from-pypi-pre-build)
  - [Manually Build and Install it Yourself](#manually-build-and-install-it-yourself)
- [:boom: Usage](#boom-usage)
- [:pencil: Exam Creation](#pencil-exam-creation)
  - [Examfile Format](#examfile-format)
  - [Exam File Structure](#exam-file-structure)
  - [Exam File Section: `exam`](#exam-file-section-exam)
    - [Example](#example)
  - [Exam File Section: `questions`](#exam-file-section-questions)
    - [Answer Selection](#answer-selection)
    - [Example](#example-1)
- [:bust_in_silhouette: Contributors](#bust_in_silhouette-contributors)
- [:computer: Development Notes](#computer-development-notes)
- [Licence](#licence)


<!-- ################################################ -->


# :fast_forward: Quick Start

```bash
# 1. Install it with pip package manager
pip install exam-terminal

# 2. Checkout the help
exam-terminal --help

# 3. Try out a sample exam
exam-terminal --sample

# 4. Try a remote sample exam
exam-terminal --examfile https://raw.githubusercontent.com/ismet55555/exam-terminal/master/exam_terminal/exams/sample_exam.yml

# Make and load your own exams using YAML format (See below)
```


<!-- ################################################ -->


# :thumbsup: Compatibility
As of now the following Python 3 versions are tested and supported:
  - Python 3.6, 3.7, 3.8, 3.9

For the following platforms:
  - OSX, Windows, Linux (Debian based)

To check which python version you have, open a terminal and type `python --version`


<!-- ################################################ -->


# :rocket: Installation

## Install It From PYPI (pre-build)

1.  Ensure internet connection
2.  Open up a terminal (or PowerShell) on your computer
3.  Ensure python is installed and has compatible version
    -  `python --version`
    - If it is not, install it. [Human Readable Guide](https://realpython.com/installing-python/)
4.  Ensure that `pip`, `setuptools`, and `wheel` are installed an up to date
    - `python -m pip install --upgrade pip setuptools wheel`
5. Install that `exam-terminal` from PYPI
    - `pip install exam-terminal`

## Manually Build and Install it Yourself

These following steps are useful if you do not have access to the internet on a particular machine.

1. Download/Clone this entire `exam-terminal` GitHub repository
2. Copy it to some temporary location on the computer you wish to install `exam-terminal` on (ie. Downloads)
3. Open up a terminal (or PowerShell) on your computer
4. Use the `cd` command to change directory into the `exam-terminal` directory
   -  Example: `cd /home/username/Downloads/exam-terminal`
5.  Ensure python is installed and has compatible version
    -  `python --version`
    - If it is not, install it. [Human Readable Guide](https://realpython.com/installing-python/)
6.  Ensure that `pip`, `setuptools`, and `wheel` are installed an up to date
    - `python -m pip install --upgrade pip setuptools wheel`
7. Install that `exam-terminal`
    - `python setup.py install`


<!-- ################################################ -->


# :boom: Usage

To load a local exam file located on your computer, or load a remote exam file located somewhere on the internet, use the `--examfile` or `-e` option flag.

If the file location contains a space, please use single or double quotes

Examples:
```bash
# Locally stored exam file
exam-terminal --examfile home/USERNAME/Downloads/examfile.yml
exam-terminal --examfile "C:\Users\YOU\My Stuff\algebra_exam.yml"

# Remotely requested exam file
exam-terminal -examfile https://raw.githubusercontent.com/ismet55555/exam-terminal/master/exam_terminal/exams/sample_exam.yml
```

**NOTE**: For help enter `exam-terminal --help`


<!-- ################################################ -->


# :pencil: Exam Creation

Exams are described within examfiles. A full example of an exam file can be seen here: [exam file](exam_terminal/exams/sample_exam.yml)

## Examfile Format

Exam description files are made using the YAML file format (`.yml` or `.yaml`), human-readable structured data format. If you are not familiar with YAML, there are lots of sources explaining it, [here is one](https://blog.stackpath.com/yaml/#:~:text=Definition,used%20to%20write%20configuration%20files.). An example of a examfile description in YAML format [can be viewed here](exam_terminal/exams/sample_exam.yml).

The exam file should be named with the `.yml` or `.yaml` file extension.

## Exam File Structure

Examfiles have two major sections:

  1. `exam` - General information about the entire exam. This includes info like exam title or allowed exam time
  2. `questions` - Information/Description for each question. This section includes each question and available selections for that question.
  

An outline of the examfile looks like this:

```yaml
exam:
  ...
questions:
  - question: ...
    selection:
      - ...
      - ...
  - question: ...
    selection:
      - ...
      - ...
  - ...
```

## Exam File Section: `exam`

This section describes the general information about the exam. The following are the available exam descriptions.

**NOTE**: _As of now all of the exam descriptions are required_

| Item                      	| Description                                         	| Example                                    	|
|---------------------------	|-----------------------------------------------------	|--------------------------------------------	|
| `exam_title`              	| The general title of the exam                       	| `AWS Kiwi Practice Exam`                   	|
| `exam_description`        	| A longer more detailed description of the exam      	| `This exam assess your knowledge on kiwis` 	|
| `exam_author`             	| The name of the person or entity that made the exam 	| `Pappa McJameson`                          	|
| `exam_edit_date`          	| The date when the exam was last edited              	| `01/01/1970`                               	|
| `exam_allwed_time`        	| Total exam time allowed                             	| `120`                                      	|
| `exam_allowed_time_units` 	| The time units that describe `exam_allowed_time`    	| `seconds`                                  	|
| `exam_passing_score`      	| Minimum passing score percentage for the exam       	| `70`                                       	|

### Example

```yaml
exam:
  exam_title: "The One Exam"
  exam_description: This exam will assess your ability to be the one. You chose that one pill now you gotta do work and prove you can fly around the matrix and stuff.
  exam_author: "Neo"
  exam_edit_date: "06/06/2199"
  exam_allowed_time: 240
  exam_allowed_time_units: "seconds"
  exam_passing_score: 95
...
```

## Exam File Section: `questions`

This section describes each question in the exam. The following are the available options for each question:

| Item                    	| Description                                                                    	| Example                       	|
|-------------------------	|--------------------------------------------------------------------------------	|-------------------------------	|
| `question`              	| Question text shown to the exam taker                                          	| `What's your favorite color?` 	|
| `question_allowed_time` 	| (Optional) Total time allowed for the specific question in seconds             	| `60`                          	|
| `selection`             	| List of answer selections for the user.<br>Correct answers denoted by `: true` 	| `- green`<br>`- black: true`  	|

### Answer Selection

To denoted the correct answer in the `selection` section, simply add at `: true` to the end of the selection. You can have more than one correct answer, that is, multiple `: true` denoted questions.

### Example

```yaml
...
questions:
  - question: What is your hobby?
    selection:
      - Politics
      - Programming: true
      - TV
      - Chillin: true
      - Reading: true
...
```
**NOTE**: If there is more than one correct (`true`) answer, the question automatically becomes a multi-answer question, allowing the exam taker to select multiple selections.


<!-- ################################################ -->


# :bust_in_silhouette: Contributors
**Ismet Handžić** - GitHub: [@ismet55555](https://github.com/ismet55555)


<!-- ################################################ -->


# :computer: Development Notes
If you are eying this repo and thinking "Hey this is kind of neat, I'd love to add a few things", well this is your chance :-)

There is definetly work to be done. If you don't have a genius great idea for the next big change, there is a [`TODO.md`](TODO.md) file which outlines some changes, features, and fixes that would be nice to have.

For some guides on how to help out, checkout the `dev_stuff` directory.


<!-- ################################################ -->


# Licence
This project is licensed under the Apache 2.0 License - Please see the [LICENSE](LICENSE) file for details.
