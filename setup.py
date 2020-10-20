#!/usr/bin/env python3

import os
import setuptools

# Utility function to read the README file. Used for the long_description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Load packages in requirements.txt
def requirements():
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as handle:
        packages = handle.readlines()
    packages = [package.strip() for package in packages]

    # If windows, add curses for windows package
    if os.name == 'nt':
        packages.append('windows-curses')

    return packages


setuptools.setup(
    name="terminal_exam",
    version="0.0.1",
    author="Ismet Handzic",
    author_email="ismet.handzic@gmail.com",
    maintainer="Ismet Handzic",
    description="A terminal-based exam, text, or survey tool for educators and learners",
    license="Apache-2.0 License",
    keywords="exam quiz assessment survey teach learn",
    url="https://github.com/ismet55555/exam-terminal",
    packages=setuptools.find_packages(),
    install_requires=requirements(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: TODO",
        "License :: OSI Approved :: Apache-2.0 License",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points={"console_scripts": [
        "exam_terminal = exam_terminal.__main__:main"]},
)
