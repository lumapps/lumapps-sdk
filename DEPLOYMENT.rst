Install requireements
---------------------

python3.7 -m pip install --user -r requirements_dev.txt

Pypi release
------------

python3.7 setup.py sdist bdist_wheel

python3.7 -m twine check dist/*

python3.7 -m twine upload dist/*

Doc
---

cd documentation

./doc-deploy.sh
