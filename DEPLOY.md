### Setup environment
```
rm -rf venv
python3.8 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

### Build package
```
rm dist/lumapps-sdk* dist/lumapps_sdk*
python setup.py sdist bdist_wheel
```

### Upload to PyPI
```
twine check dist/*
twine upload dist/*
```

### Add a release on GitHub
```
git tag v0.1.17
git push origin v0.1.17
```
