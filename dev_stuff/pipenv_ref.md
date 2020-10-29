# `pipenv` Basics

Don't need pip, virtualenv, venv, or requirements.txt anymore!

Installation:

- `pip install pipenv` (or `sudo apt install pipenv`)

## Basics

- Change directory into project directory

- Create pipenv and install packages from Pipfile

  - `pipenv install [OPTIONS] [PROJECT DIRECTORY]`

  - Options:
    - Don't try to lock: `--ignore-pipfile`
    - Actively editable env: `-e`
    - Python Major version: `--two` or `--three`
    - Use specific python version: `--python 3.6`
    - No standard output: `--quiet`
  - Development Example
    - `pipenv install --three --python 3.6 --dev -e .`
    - **NOTE**: Will include the `[dev-packages]` section in `Pipfile`
  - Production Example
    - `pipenv install --ignore-pipfile`

- Installing additional packages
  - `pipenv install <PACKAGE NAME>`
- Activate the created pipenv virtual environment

  - `pipenv shell`

- Locking the current pipenv dependencies and package versions

  - `pipeenv lock`
  - **NOTE**: If `Pipfile` changes, this will happen automatically

- Upgrade packages

  - `pipenv update <PACKAGE NAME>`

- Uninstall the development packages

  - Specific package: `pipenv uninstall <PACKAGE NAME>`
  - All development packages: `pipenv uninstall --all-dev`

- Deactivating a active pipenv (reverse `pipenv shell`)

  - Linux: `exit` or `CTRL+D`
  - Windows: `exit`

- Removing the pyenv virtual environment

  - `pipenv --rm`

- Other useful things:
  - Run single command in the created pipenv
    - `pipenv run [COMMAND]`
    - Example: `pipenv run python main.py`
  - Install all packages specified in `Pipfile.lock`
    - `pipenv sync`
  - Find out what packages have changed upstream and update
    - Runs lock than sync
    - `pipenv update --outdated`
