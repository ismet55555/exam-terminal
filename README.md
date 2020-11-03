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

The exam-terminal is a terminal-based assessment tool. It can potentially be used for making and taking practice exams, deliver quizes, or collect a survey.

The results include your general exam score, some basic statistics, and the ability to export your results to a PDF documment.

## :eyeglasses: Overview

* [Quick Start](#fast_forward-quick-start)
* [Compatibility](#thumbsup-compatibility)
* [Installation](#rocket-installation)
* [Exam Creation](#pencil-exam-creation)
* [Contributors](#bust_in_silhouette-contributors)
* [Development Notes](#computer-Development-Notes)
* [Licence](#licence)


## :fast_forward: Quick Start

```bash
# Install it
pip install exam-terminal

# Quick checkout of the help
exam-terminal --help

# Try out a sample exam
exam-terminal --sample

# Make your own exams using YAML format (See below)
```


## :thumbsup: Compatibility
As of now the following Python 3 versions are tested and supported:
  - Python 3.6, 3.7, 3.8, 3.9

For the following platforms:
  - OSX, Windows, Linux (Debian based)

To check which python version you have, open a terminal and type `python --version`


## :rocket: Installation

### Get It From PYPI
```bash
pip install exam-terminal
```
### _(If Needed)_ Install pip, setuptools, and wheel

```bash
python -m pip install --upgrade pip setuptools wheel
```

## :pencil: Exam Creation

Exams are made using the YAML file format.

See example here:  [`sample_exam.yml`](exam_terminal/exams/sample_exam.yml)

_TODO: Section work in progress_





---
## :bust_in_silhouette: Contributors
**Ismet Handžić** - GitHub: [@ismet55555](https://github.com/ismet55555)

## :computer: Development Notes
If you are eying this repo and thinking "Hey this is kind of neat, I'd love to add a few things", well this is your chance :-)

There is definetly work to be done. If you don't have a genius great idea for the next big change, there is a [`TODO.md`](TODO.md) file which outlines some changes, features, and fixes that would be nice to have.

For some guides on how to help out, checkout the `dev_stuff` directory.

## Licence
This project is licensed under the Apache 2.0 License - Please see the [LICENSE](LICENSE) file for details.
