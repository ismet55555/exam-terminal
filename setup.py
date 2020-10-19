#!/usr/bin/env python3

import os
import setuptools

# Utility function to read the README file. Used for the long_description
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def requirements():
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as handle:
        return handle.readlines()

setuptools.setup(
    name = "terminal-exam",
    version = "0.0.1",
    author = "Ismet Handzic",
    author_email = "ismet.handzic@gmail.com",
    maintainer = "Ismet Handzic",
    description = ("An demonstration of how to create, document, and publish "
                   "to the cheese shop a5 pypi.org."),
    license = "Apache-2.0 License",
    keywords = "example documentation tutorial",
    url = "http://packages.python.org/an_TODO",
    packages = setuptools.find_packages(),
    install_requires=requirements(),
    long_description=read('README'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: TODO",
        "License :: OSI Approved :: TODO",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points={"console_scripts": ["exam-terminal = exam-terminal.__main__:main"]},
)