from setuptools import setup, find_packages

from lumapps.api import __version__, __pypi_packagename__


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r") as f:
    readme = f.read()
setup(
    name=__pypi_packagename__,
    version=__version__,
    author="LumApps",
    url="https://github.com/lumapps/lumapps-sdk",
    packages=find_packages(exclude=["documentation", "tests", "examples"]),
    include_package_data=True,
    license="MIT",
    description="LumApps SDK for Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=parse_requirements("requirements.txt"),
    python_requires=">=3.6",
    keywords="lumapps sdk",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    project_urls={
        "Documentation": "https://lumapps.github.io/lumapps-sdk/",
        "Source": "https://github.com/lumapps/lumapps-sdk",
        "Issues": "https://github.com/lumapps/lumapps-sdk/issues",
        "CI": "https://circleci.com/gh/lumapps/lumapps-sdk",
    },
    entry_points={"console_scripts": ["lac=lumapps.api.cli:main"]},
)