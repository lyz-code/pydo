"""Define the terminal user interface."""

from typing import Any, Callable, List, Optional, Union

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import (
    Container,
    HorizontalAlign,
    HSplit,
    VerticalAlign,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import AnyDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.styles import Style

# Helper functions


class Table(HSplit):
    """Define a table.

    Args:
        header
        data: Data to print
        handler: Called when the row is clicked, no parameters are passed to this
            callable.
    """

    def __init__(
        self,
        data: Any,
        window_too_small: Optional[Container] = None,
        align: VerticalAlign = VerticalAlign.JUSTIFY,
        padding: AnyDimension = 0,
        padding_char: Optional[str] = None,
        padding_style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        z_index: Optional[int] = None,
        modal: bool = False,
        key_bindings: Optional[KeyBindingsBase] = None,
        style: Union[str, Callable[[], str]] = "",
    ) -> None:
        """Initialize the widget."""
        self.data = data
        # rows = [MultiColumnRow(row) for row in self.data]
        rows = [
            MultiColumnRow(data[0]),
            MultiColumnRow(data[1], alternate=True),
            MultiColumnRow(data[2]),
            MultiColumnRow(data[2], alternate=True),
        ]

        super().__init__(
            children=rows,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=padding_style,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )


class MultiColumnRow(VSplit):
    """Define row.

    Args:
        text: text to print
    """

    def __init__(
        self,
        data: Optional[List[str]] = None,
        alternate: bool = False,
        window_too_small: Optional[Container] = None,
        align: HorizontalAlign = HorizontalAlign.JUSTIFY,
        padding: AnyDimension = 2,
        padding_char: Optional[str] = " ",
        padding_style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        z_index: Optional[int] = None,
        modal: bool = False,
        key_bindings: Optional[KeyBindingsBase] = None,
        style: Union[str, Callable[[], str]] = "",
    ) -> None:
        """Initialize the widget."""
        if data is None:
            data = []
        self.data = data

        def get_style() -> str:
            if get_app().layout.has_focus(self):
                return "class:row.focused"
            else:
                return "class:row"

        def get_style_alternate() -> str:
            if get_app().layout.has_focus(self):
                return "class:row.alternate.focused"
            else:
                return "class:row.alternate"

        if alternate:
            style = get_style_alternate
        else:
            style = get_style

        columns = [
            Window(
                FormattedTextControl(self.data[0], focusable=True),
                style=style,
                always_hide_cursor=True,
                dont_extend_height=True,
                dont_extend_width=True,
                wrap_lines=True,
            ),
            Window(
                FormattedTextControl(self.data[1], focusable=False),
                style=style,
                always_hide_cursor=True,
                dont_extend_height=True,
                wrap_lines=True,
            ),
        ]
        # self.window.children[1].width = 10
        super().__init__(
            children=columns,
            window_too_small=window_too_small,
            align=align,
            padding=padding,
            padding_char=padding_char,
            padding_style=style,
            width=width,
            height=height,
            z_index=z_index,
            modal=modal,
            key_bindings=key_bindings,
            style=style,
        )


# Layout

layout = Table(
    [
        ["Test1", "Description"],
        [
            "Test2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa aaaaaaaaaaaaaaaaaaaaaaaaaaa a",
        ],
        ["Test3", "Description 2"],
    ]
)

# Key bindings

kb = KeyBindings()

kb.add("j")(focus_next)
kb.add("k")(focus_previous)


@kb.add("c-c", eager=True)
@kb.add("q", eager=True)
def exit_(event: KeyPressEvent) -> None:
    """Exit the user interface."""
    event.app.exit()


# Styles

style = Style(
    [
        ("row", "bg:#002b36 #657b83"),
        ("row.focused", "#268bd2"),
        ("row.alternate", "bg:#073642 #657b83"),
        ("row.alternate.focused", "#268bd2"),
    ]
)
# Application

# ignore: it asks for the type annotation of app, but I haven't found it
app = Application(  # type: ignore
    layout=Layout(layout),
    full_screen=True,
    key_bindings=kb,
    style=style,
    color_depth=ColorDepth.DEPTH_24_BIT,
)

app.run()
