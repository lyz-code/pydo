from setuptools import find_packages
from setuptools import setup

from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        try:
            os.makedirs('~/.local/share/pydo')
            os.system('pydo install')
        except FileExistsError:
            print('Installation directory already exits')


class PostDevelopCommand(develop):
    """Post-installation for develop mode."""
    def run(self):
        develop.run(self)
        try:
            os.makedirs('~/.local/share/pydo')
            os.system('pydo install')
        except FileExistsError:
            print('Installation directory already exits')

class PostEggInfoCommand(egg_info):
    """Post-installation for egg_info mode."""
    def run(self):
        egg_info.run(self)
        try:
            os.makedirs('~/.local/share/pydo')
            os.system('pydo install')
        except FileExistsError:
            print('Installation directory already exits')

__version__ = '0.1.0'

setup(
    name='pydo',
    version=__version__,
    description='CLI task manager built with Python and SQLite.',
    author='Lyz',
    author_email='lyz@riseup.net',
    license='GPLv3',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=('tests',)),
    package_data={'pydo': [
        'migrations/*',
        'migrations/versions/*',
    ]},
    entry_points={'console_scripts': ['pydo = pydo:main']},
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
        'egg_info': PostEggInfoCommand,
    },
    install_requires=[
        "argcomplete>=1.11.1",
        "SQLAlchemy>=1.3.11",
        "alembic>=1.3.1",
        "python-dateutil>=2.8.1",
        "tabulate>=0.8.7",
        "ulid-py>=0.0.12",
    ]
)
