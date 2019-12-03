### Setup environment
- rm -rf venv
- python3.8 -m venv venv
- source venv/bin/activate
- python -m pip install -U pip pylint pytest flake8
- python -m pip install -r requirements.txt
- python -m pip install -r requirements_dev.txt

### Build package
- rm dist/lumapps-sdk* dist/lumapps_sdk*
- python setup.py sdist bdist_wheel

### Upload to PyPI
- python -m twine check dist/*
- python -m twine upload dist/*

### Add a release on GitHub
- git tag v0.1.17
- git push origin v0.1.17

### Update documentation
- cd documentation
- ./doc-deploy.sh