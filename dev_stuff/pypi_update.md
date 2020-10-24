# PYPI Package Update

- Clean previous build
  - `python3 setup.py clean --all`

- Create wheel build and 
  - `python3 setup.py sdist bdist_wheel`

- Upload to PYPI
  - TestPYPI: `python3 -m twine upload --repository testpypi dist/*` 
  - PYPI: `twine upload dist/*`





