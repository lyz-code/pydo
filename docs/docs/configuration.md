---
title: Configuration
date: 20200301
author: Lyz
---

All configuration is stored in the database. By default, `pydo` uses a SQLite
database in `~/.local/share/pydo/main.db`, but you can define another connection
with the `PYDO_DATABASE_URL` environmental variable, such as
`sqlite:///absolute_path_to_file.md`.

When you execute `pydo install` the [initial
schema](https://github.com/lyz-code/pydo/blob/master/pydo/manager.py#L18) is
configured.

Until we [have a better solution](https://github.com/lyz-code/pydo/issues/13),
the only way to modify the configuration is to manually edit the `config` table
of the database. You can do so with different programs, but I suggest
[litecli](https://litecli.com/).
