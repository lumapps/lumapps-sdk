
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lumapps-sdk",
    version="1.1.3b2",
    author="LumApps",
    license="MIT",
    description="LumApps SDK",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["Authlib==0.15.*", "httpx==0.16.*", "python-slugify==4.0.*"],
    python_requires=">=3.6",
    url="https://github.com/lumapps/lumapps-sdk",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["lah=lumapps_api.cli:main"]},
)