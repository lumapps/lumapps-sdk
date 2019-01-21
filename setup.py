from io import open
from setuptools import setup, find_packages
from lumapps.config import __version__, __pypi_packagename__


def read_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return content


setup(
    name=__pypi_packagename__,
    version=__version__,
    author="LumApps",
    url="https://github.com/lumapps/lumapps-sdk",
    packages=find_packages(exclude=["documentation", "tests"]),
    include_package_data=True,
    license="MIT",
    description="Lumapps SDK for Python",
    long_description=read_file("README.rst"),
    long_description_content_type="text/x-rst",
    install_requires=[
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "python-slugify",
        "cryptography",
        "pathlib2",
        "repoze.lru",
        "enum34",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
    ],
    project_urls={
        "Documentation": "https://lumapps.github.io/lumapps-sdk/",
        "Source": "https://github.com/lumapps/lumapps-sdk",
        "Issues": "https://github.com/lumapps/lumapps-sdk/issues",
        "CI": "https://circleci.com/gh/lumapps/lumapps-sdk",
    },
    entry_points={
        "console_scripts": ["client=lumapps.cli:main", "lac=lumapps.cli:main"]
    },
)
