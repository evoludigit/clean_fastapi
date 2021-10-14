from __future__ import annotations
from dataclasses import dataclass
from anytree import NodeMixin
from typing import Optional
from slugify import slugify

pattern_ltree_compatible = "[^-a-z0-9_]+"

def identifier_from_string(a_string: str) -> str:
    return slugify(a_string, regex_pattern=pattern_ltree_compatible, separator="_")

@dataclass
class TodoInfo():
    name: str
    due_date: str
    description: str


@dataclass
class Todo(NodeMixin):
    """
    implements materialized path
    """
    info: TodoInfo
    parent_todo: Optional[Todo]
    def __post_init__(self):
        this_todo_identifier: str = f"{identifier_from_string(self.info.name)}"
        if not self.parent_todo:
            self.identifier = this_todo_identifier
        else:
            self.identifier =  ".".join([self.parent_todo.identifier, this_todo_identifier])
