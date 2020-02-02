from setuptools import find_packages
from setuptools import setup

from pydo import __version__


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
    install_requires=[
        "SQLAlchemy==1.3.11",
        "alembic==1.3.1",
    ]
)
