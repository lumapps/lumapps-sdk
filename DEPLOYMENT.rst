
Doc
---

cd documentation

./deploy.sh

Pypi release
------------

python setup.py sdist bdist_wheel

twine check dist/*

twine upload dist/*
