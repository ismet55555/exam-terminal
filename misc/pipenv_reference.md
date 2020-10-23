# pipenv basics

Don't need pip, virtualenv, venv, or requirements.txt anymore!

`pip install pipenv`

## Basic Usage
- Clone project
- cd into project

## For Development

- Create pipenv and install packages from Pipfile
  - `pipenv install --three --dev -e .`

- Installing additional packages
  - `pipenv install <PACKAGE NAME>`
  
- Activate the current pipenv virtual environment
  - `pipenv shell`


- Locking the current pipenv dependencies and package versions
  - `pipeenv lock`

- Find out what packages have changed upstream (upgraded)
  - `pipenv update --outdated`

- Upgrade packages
  - `pipenv update <PACKAGE NAME>`

- Uninstall the development packages
  - `pipenv uninstall --all-dev`

- Removing the pyenv virtual environment
  - `pipenv --rm`

## For Production

- TODO