Install requireements
---------------------

python3.7 -m pip install --user -r requirements_dev.txt

Doc
---

cd documentation

./doc-deploy.sh

Pypi release
------------

python setup.py sdist bdist_wheel

twine check dist/*

twine upload dist/*
