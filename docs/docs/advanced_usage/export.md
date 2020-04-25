---
title: Export
date: 20200425
author: Lyz
---

Use the `export` command if you want to dump your database into json format.
It can be useful to do migrations of database schema in SQLite as it doesn't
support the alter table operation, do operations in your data that are not yet
supported in `pydo` or if you want to extract all your information to import it
in another task manager.
