---
title: Sorting
date: 20211007
author: Lyz
---

`pydo` lets you sort the contents of any report with the `sort:` task filter. By
default, the reports are sorted increasingly by the task id.

```bash
$: pydo open
     ╷                                  ╷
  ID │ Description                      │ Pri
╺━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━╸
  0  │ First task with medium priority  │ 3
  1  │ Second task with medium priority │ 3
  2  │ Third task with low priority     │ 1
     ╵                                  ╵
```

If you want to sort the tasks increasingly by priority instead, you could use:

```bash
$: pydo open sort:+priority
     ╷                                  ╷
  ID │ Description                      │ Pri
╺━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━╸
  2  │ Third task with low priority     │ 1
  0  │ First task with medium priority  │ 3
  1  │ Second task with medium priority │ 3
     ╵                                  ╵
```

To sort by more than one criteria, separate them by commas. For example, if you
want to sort increasingly by priority and then decreasingly by id, use:

```bash
$: pydo open sort:+priority,-id_
     ╷                                  ╷
  ID │ Description                      │ Pri
╺━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━╸
  2  │ Third task with low priority     │ 1
  1  │ Second task with medium priority │ 3
  0  │ First task with medium priority  │ 3
     ╵                                  ╵
```

!!! warning "To sort by ID you need to use `id_` instead of `id`."
