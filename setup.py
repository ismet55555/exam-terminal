#!/usr/bin/env python3

import os
import setuptools

# Package version number (Updated via bumpversion)
__version__ = "0.2.0"


def read(fname):
    """Utility function to read the README file. Used for the long_description"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements():
    """Load packages in requirements.txt"""
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as handle:
        packages = handle.readlines()
    packages = [package.strip() for package in packages]

    return packages


setuptools.setup(
    name="exam-terminal",
    version=__version__,
    author="Ismet Handzic",
    author_email="ismet.handzic@gmail.com",
    maintainer="Ismet Handzic",
    description="A terminal-based exam, text, or survey tool for educators and learners",
    keywords="exam quiz assessment survey teach learn",
    url="https://github.com/ismet55555/exam-terminal",
    packages=setuptools.find_packages(),
    install_requires=requirements(),
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    setup_requires=['wheel'],
    py_modules=["exam_terminal"],
    entry_points={"console_scripts": [
        "exam-terminal = exam_terminal.__main__:main"]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Education :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Environment :: Console",
        "Environment :: Console :: Curses",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
