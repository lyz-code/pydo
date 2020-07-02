---
title: Reports
date: 20211007
author: Lyz
---

`pydo` comes with some configured reports, such as `open`, `closed`,
`recurring`, `overdue`, `frozen`. Each of them accepts a task
filter that let's you do more specific queries over the content shown by those
reports. Even so, you may want to create your own reports, or change the
existing ones.

All report configuration is saved in the config file (by default at
`~/.local/share/pydo/config.yaml`) under the key `task_reports`. Each of them
has the following properties:

* `report_name`: It's the key that identifies the report.
* `columns`: Ordered list of task attributes to print.
* `filter`: Dictionary of task properties that narrow down the tasks you
    want to print.
* `sort`: Ordered list of criteria used to sort the tasks.

To create a new report that shows the open tasks of the area `health` and
priority `5`, sorted descending by priority, edit your config file as the next
snippet:

```yaml
reports:
  task_reports:
    important_health:
      filter:
        active: true
        type: task
        area: health
        priority: 5
      sort:
        - "-priority"
      columns:
        - id_
        - description
        - area
        - priority
        - tags
        - due
        - parent_id
```
