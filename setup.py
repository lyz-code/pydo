"""Python package building configuration."""

import logging
import os
import re
import shutil
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

log = logging.getLogger(__name__)

# Avoid loading the package to extract the version
with open("src/pydo/version.py") as fp:
    version_match = re.search(r'__version__ = "(?P<version>.*)"', fp.read())
    if version_match is None:
        raise ValueError("The version is not specified in the version.py file.")
    version = version_match["version"]


with open("README.md", "r") as readme_file:
    readme = readme_file.read()


setup(
    name="pydo",
    version=version,
    description="CLI task manager built with Python and SQLite.",
    author="Lyz",
    author_email="lyz-code-security-advisories@riseup.net",
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/lyz-code/pydo",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"pydo": ["py.typed"]},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Natural Language :: English",
    ],
    entry_points="""
        [console_scripts]
        pydo=pydo.entrypoints.cli:cli
    """,
    install_requires=[
        "click",
        "click-default-group",
        "repository-orm",
        "rich",
        "python-dateutil",
        "ulid-py",
        "ruyaml",
    ],
)

try:
    data_directory = os.path.expanduser("~/.local/share/pydo")
    os.makedirs(data_directory)
    log.info("Data directory created")
except FileExistsError:
    log.info("Data directory already exits")

config_path = os.path.join(data_directory, "config.yaml")
if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
    log.info(
        "Configuration file already exists, check the documentation "
        "for the new version changes."
    )
else:
    shutil.copyfile("assets/config.yaml", config_path)
    log.info("Copied default configuration template")
