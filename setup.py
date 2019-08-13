#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import setup, find_packages, Extension
from distutils.util import convert_path
import os

here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, "h8mail/utils/version.py")).read())

with open("PyPi.rst") as readme_file:
    readme = readme_file.read()

# with open("HISTORY.rst") as history_file:
#     history = history_file.read()

requirements = ["requests"]

setup_requirements = ["requests"]

test_requirements = ["requests"]

setup(
    author="khast3x",
    author_email="k@khast3x.club",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
    ],
    description="Email OSINT and password breach hunting. Use h8mail to find passwords through different breach and reconnaissance services, or the infamous Breached Compilation torrent",
    install_requires=requirements,
    license="BSD license",
    # long_description_content_type="text/markdown",
    long_description=readme + "\n\n",
    # long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="h8mail",
    name="h8mail",
    packages=find_packages(),
    entry_points={"console_scripts": ["h8mail = h8mail.__main__:main"]},
    setup_requires=setup_requirements,
    url="https://github.com/khast3x/h8mail",
    version=__version__,
    zip_safe=False,
)
