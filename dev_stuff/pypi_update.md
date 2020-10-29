# Python Package Index (PYPI) Update

- Bump the package version number
  - Version format: `MAJOR.MINOR.PATCH`
  - `bumpversion major`, `bumpverison minor`, or `bumpversion patch`
  - Run inside directory containing file `.bumpversion.cfg`

- Clean any previous build
  - Build: `python3 setup.py clean --all`
  - Dist: `rm -rf dist`  (Windows: `rm -force dist`)

- Create source distribution and pure python wheels build
  - `python3 setup.py sdist bdist_wheel`

- Upload to PYPI
  - TestPYPI:
    - This is preferred for development work 
    - https://test.pypi.org/project/exam-terminal/
    - `twine upload -r testpypi dist/*` 
  - PYPI: 
    - The real deal. This is what users will download from
    - https://pypi.org/project/exam-terminal/
    - `twine upload dist/*`





