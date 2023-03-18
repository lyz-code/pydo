"""TEst."""

from typing import Dict, Iterable, List, Tuple, TypeVar

from prompt_toolkit.layout.containers import HSplit
from pydantic import BaseModel  # noqa: E0611

T = TypeVar("T", int, float, complex)

Vec = Iterable[Tuple[T, T]]

RowData = TypeVar("RowData", "BaseModel", Dict[str, str], List[str])
TableData = List[RowData]


class TestClass(HSplit):
    """test."""

    def __init__(self, vect: Vec = None, table: TableData = None):
        """test."""
        self.vect = vect
        self.table = table
