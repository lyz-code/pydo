"""Define the object models for the views."""

from typing import List

from pydantic import BaseModel, Field  # noqa: E0611
from repository_orm import EntityNotFoundError
from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table


class Colors(BaseModel):
    """Define the program colors."""

    background_1: str = "#073642"
    background_2: str = "#002b36"
    foreground_1: str = "#657b83"
    foreground_2: str = "#586e75"
    yellow: str = "#b58900"
    orange: str = "#cb4b16"
    red: str = "#dc322f"
    magenta: str = "#d33682"
    violet: str = "#6c71c4"
    blue: str = "#268bd2"
    cyan: str = "#2aa198"
    green: str = "#859900"


class Report(BaseModel):
    """Manage the data to print."""

    labels: List[str]
    data: List[List[str]] = Field(default_factory=list)
    colors: Colors = Colors()

    def _remove_null_columns(self) -> None:
        """Remove the columns that have all None items from the report_data."""
        for column in reversed(range(0, len(self.labels))):
            # If all entities have the None attribute value, remove the column from
            # the report.
            column_used = False
            for row in range(0, len(self.data)):
                if self.data[row][column] not in [None, ""]:
                    column_used = True

            if not column_used:
                [row.pop(column) for row in self.data]
                self.labels.pop(column)

    def add(self, data: List[str]) -> None:
        """Add a row of data to the report."""
        self.data.append(data)

    def print(self) -> None:
        """Print the report."""
        self._remove_null_columns()

        if len(self.data) == 0:
            raise EntityNotFoundError("The report doesn't have any data to print")

        table = Table(
            box=box.MINIMAL,
            header_style=Style(color=self.colors.violet),
            style=Style(color=self.colors.background_1),
            border_style=Style(color=self.colors.background_1),
            row_styles=[
                Style(color=self.colors.foreground_1),
                Style(color=self.colors.foreground_2),
            ],
        )

        for label in self.labels:
            table.add_column(label)

        for row in self.data:
            row = [str(element) for element in row]
            table.add_row(*row)

        console = Console()
        console.print(table)
