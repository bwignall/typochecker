# Useful resource: https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="typochecker",
    version="0.1.1",
    description="A tool to help (semi-)automatically find typos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bwignall/typochecker",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console" "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="typos spellchecker",
    packages=find_packages(where="."),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    install_requires=[],
    extras_require={"test": ["coverage", "flake8", "nose"],},
    package_data={
        "corrector": [
            "data/extra_endings.txt",
            "data/wikipedia_common_misspellings.txt",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/bwignall/typochecker/issues",
        "Source": "https://github.com/bwignall/typochecker",
    },
)
