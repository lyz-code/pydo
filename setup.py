"""Python package building configuration."""

import logging
import re
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
    name="py-do",
    version=version,
    description="Free software command line task manager built in Python.",
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
