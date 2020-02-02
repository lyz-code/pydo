# Pydo

`pydo` is a CLI task manager built with Python and SQLite.

## Install

```bash
pip3 install git+git://github.com/lyz-code/pydo
sudo apt install sqlite3
mkdir ~/.local/share/pydo/
sqlite3 ~/.local/share/pydo/main.db # Default path of the database
pydo install
```
If you like to change the default path of the database, then set the enviroment variable `PYDO_DATABASE_URL` to whatever path you want to use

## Commands
* `pydo add <name>`:&nbsp;Add a task to the database
* `pydo del <id>`:&nbsp; Delete an existing task from the database
* `pydo list`:&nbsp; List existing tasks. Calling `pydo` without arguments also lists existing tasks.
* `pydo -h` or `pydo --help` shows the help message