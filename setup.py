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
        import pydo

        pydo.main(["install"])


class PostEggInfoCommand(egg_info):
    """Post-installation for egg_info mode."""

    def run(self):
        egg_info.run(self)
        try:
            data_directory = os.path.expanduser("~/.local/share/pydo")
            os.makedirs(data_directory)
            log.info("Data directory created")
        except FileExistsError:
            log.info("Data directory already exits")

        config_path = os.path.join(data_directory, 'config.yaml')
        if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
            log.info(
                "Configuration file already exists, check the documentation "
                "for the new version changes."
            )
        else:
            shutil.copyfile('assets/config.yaml', config_path)
            log.info("Copied default configuration template")
        import pydo

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
    package_data={"pydo": ["migrations/*", "migrations/versions/*"]},
    entry_points={"console_scripts": ["pydo = pydo:main"]},
    cmdclass={
        "install": PostInstallCommand,
        "egg_info": PostEggInfoCommand,
    },
    setup_requires=[
        "alembic>=1.3.1",
        "argcomplete>=1.11.1",
        "SQLAlchemy>=1.3.11",
        "python-dateutil>=2.8.1",
        "tabulate>=0.8.7",
        "ulid-py>=0.0.12",
    ],
    install_requires=[
        "alembic>=1.3.1",
        "argcomplete>=1.11.1",
        "python-dateutil>=2.8.1",
        "ruamel.yaml>=0.16.10",
        "SQLAlchemy>=1.3.11",
        "tabulate>=0.8.7",
        "ulid-py>=0.0.12",
    ],
)
