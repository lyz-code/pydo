import logging
import os

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install
from sqlalchemy.orm import sessionmaker

import pydo


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        logger = logging.getLogger("main")
        try:
            data_directory = os.path.expanduser("~/.local/share/pydo")
            os.makedirs(data_directory)
        except FileExistsError:
            logger.info("Data directory already exits")
        pydo.main(["install"])


class PostDevelopCommand(develop):
    """Post-installation for develop mode."""

    def run(self):
        develop.run(self)
        logger = logging.getLogger("main")
        try:
            data_directory = os.path.expanduser("~/.local/share/pydo")
            os.makedirs(data_directory)
        except FileExistsError:
            logger.info("Data directory already exits")
        pydo.main(["install"])


class PostEggInfoCommand(egg_info):
    """Post-installation for egg_info mode."""

    def run(self):
        egg_info.run(self)
        logger = logging.getLogger("main")
        try:
            data_directory = os.path.expanduser("~/.local/share/pydo")
            os.makedirs(data_directory)
        except FileExistsError:
            logger.info("Data directory already exits")
        pydo.main(["install"])


__version__ = "0.1.0"

setup(
    name="pydo",
    version=__version__,
    description="CLI task manager built with Python and SQLite.",
    author="Lyz",
    author_email="lyz@riseup.net",
    license="GPLv3",
    long_description=open("README.md").read(),
    packages=find_packages(exclude=("tests",)),
    package_data={"pydo": ["migrations/*", "migrations/versions/*",]},
    entry_points={"console_scripts": ["pydo = pydo:main"]},
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
        "egg_info": PostEggInfoCommand,
    },
    install_requires=[
        "argcomplete>=1.11.1",
        "SQLAlchemy>=1.3.11",
        "alembic>=1.3.1",
        "python-dateutil>=2.8.1",
        "tabulate>=0.8.7",
        "ulid-py>=0.0.12",
    ],
)
