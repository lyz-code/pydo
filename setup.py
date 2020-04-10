from setuptools import find_packages
from setuptools import setup

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
    install_requires=[
        "argcomplete>=1.11.1",
        "SQLAlchemy>=1.3.11",
        "alembic>=1.3.1",
        "python-dateutil>=2.8.1",
        "tabulate>=0.8.7",
        "ulid-py>=0.0.12",
    ]
)
