from io import open
from setuptools import setup, find_packages


def read_file(file_path):
    with open(file_path, "r") as f:
        content = f.read()
    return content


setup(
    name="lumapps-sdk",
    version=read_file("lumapps_api_client/version.py"),
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
        "console_scripts": [
            "lumapps_api_client=lumapps_api_client.cli:main",
            "lac=lumapps_api_client.cli:main",
        ]
    },
)
