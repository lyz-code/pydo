import logging
import os
import shutil

from setuptools import find_packages, setup
from setuptools.command.egg_info import egg_info
from setuptools.command.install import install

log = logging.getLogger(__name__)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)

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


class PostEggInfoCommand(egg_info):
    """Post-installation for egg_info mode."""

    def run(self):
        egg_info.run(self)


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
    package_data={"pydo": ["migrations/*", "migrations/versions/*"]},
    cmdclass={"install": PostInstallCommand, "egg_info": PostEggInfoCommand},
    setup_requires=["alembic", "SQLAlchemy"],
    install_requires=[
        "alembic",
        "Click",
        "click-default-group",
        "ruamel.yaml",
        "SQLAlchemy",
        "tabulate",
        "ulid-py",
    ],
    entry_points="""
        [console_scripts]
        pydo=pydo.entrypoints.cli:cli
    """,
)
