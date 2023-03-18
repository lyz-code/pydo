Date: 2021-10-16

# Status
<!-- What is the status? Draft, Proposed, Accepted, Rejected, Deprecated or Superseded?
-->
Draft

# Context
<!-- What is the issue that we're seeing that is motivating this decision or change? -->


# Proposals
<!-- What are the possible solutions to the problem described in the context -->

We could use a [scroll
marging](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/simple-demos/margins.py)
if the text is too long. or use a scrollable panel (see below).

Get inspiration in the [scrollable panel
example](https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/scrollable-panes/simple-example.py)
to create the list of tasks.

To paint the different lines use the `style` argument with `class:row` and
`class:alternate_row`

Use `FormattedTextControl` to format text?
https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/split-screen.py

# Decision
<!-- What is the change that we're proposing and/or doing? -->

# Consequences
<!-- What becomes easier or more difficult to do because of this change? -->
