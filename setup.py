import sys
import os
from io import open
from setuptools import setup, find_packages

__version__ = None
with open("lumapps_api_client/version.py") as f:
    exec(f.read())

long_description = "Please see our GitHub README"
if os.path.exists("README.md"):
    long_description = open("README.md", "r", encoding="utf-8").read()


def getRequires():
    deps = []

    requirements = None
    with open("requirements.txt") as f:
        requirements = f.read().splitlines()

    return deps if requirements is None else requirements


setup(
    name="lumapps_sdk",
    version=str(__version__),
    author="Jean Sebastien SEVESTRE, Ludovic VAUGEOIS PEPIN, Salah GHAMIZI",
    author_email="js@lumapps.com",
    url="",
    packages=find_packages(include=["lumapps_api_helpers", "lumapps_api_client"]),
    include_package_data=True,
    license="MIT",
    description="Lumapps SDK for Python",
    long_description=long_description,
    install_requires=getRequires(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points={
        "console_scripts": [
            "lumapps_api_client=lumapps_api_client.cli:main",
            "lac=lumapps_api_client.cli:main",
        ]
    },
)
