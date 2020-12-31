---
title: Database Schema
date: 20200424
author: Lyz
---

The schema is defined in the
[models.py](https://github.com/lyz-code/pydo/blob/master/pydo/models.py) file
through
[SQLAlchemy](https://lyz-code.github.io/blue-book/coding/python/sqlalchemy/)
objects.

To visualize the schema we've used
[wwwsqldesigner](https://github.com/ondras/wwwsqldesigner/wiki) through their
[hosted instance](https://ondras.zarovi.cz/sql/demo/). We load the
[database_schema.xml](https://github.com/lyz-code/pydo/tree/master/pydo/migrations/sql_schema.xml)
to modify it and save it back as xml in the repo.

![](../../images/database_schema.jpg)

# How to add a new field
Rough draft of how to add a new field
* `manager.py`
  * Declare field so that pydo can parse a new command-line argument in  `_parse_agruments`
  * The new field itself must be parsed on `_parse_attribute`
* `migrations/sql_schema.xml`
* `models.py`
  * `__init__`
  * `self.new_field = field`

* `alembic revision --autogenerate -m "description commit message"`
