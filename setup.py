from setuptools import setup, find_packages

try:
    # pip >=20
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.req import parse_requirements

from lumapps.api import __version__, __pypi_packagename__


with open("README.rst", "r") as f:
    readme = f.read()
reqs = parse_requirements("requirements.txt", session=None)
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
    long_description_content_type="text/x-rst",
    install_requires=[str(r.req) for r in reqs],
    python_requires=">=3.6",
    keywords="lumapps sdk",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
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
