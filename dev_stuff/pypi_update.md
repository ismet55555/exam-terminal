# PYPI Package Update

- Clean any previous build
  - Build: `python3 setup.py clean --all`
  - Dist: `rm -rf dist`  (Windows: `rm -force dist`)

- Create source distribution and pure python wheels build
  - `python3 setup.py sdist bdist_wheel`

- Upload to PYPI
  - TestPYPI: `python3 -m twine upload --repository testpypi dist/*` 
  - PYPI: `twine upload dist/*`





