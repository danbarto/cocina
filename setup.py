#!/usr/bin/env python3
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [
    x.strip().replace("git+", "") for x in all_reqs if x.startswith("git+")
]

setup(
    name='cocina',
    version='1.0.0',
    description="Wrapper for the Sigilent Power Supply API",
    url="https://github.com/danbarto/cocina/",
    #packages=find_packages(exclude=["docs", "tests*", "examples"]),
    packages=find_packages(),
    install_requires=install_requires,
    dependency_links=dependency_links,
)
