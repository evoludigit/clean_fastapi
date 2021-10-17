import uuid

from clean.domain import model
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData
from sqlalchemy_utils import LtreeType

# https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/

metadata = MetaData()
mapper_registry = registry(metadata=metadata)


table_todo_info = Table(
    "tb_todo_info",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "pk_todo_info",
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ),
    Column("identifier", String(255)),
    Column("name", String(255)),
    Column("due_date", String(255)),
    Column("description", String(255)),
)

table_todo = Table(
    "tb_todo",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "pk_todo",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ),
    Column(
        "fk_todo_info",
        UUID(as_uuid=True),
        ForeignKey("tb_todo_info.pk_todo_info"),
    ),
    Column(
        "fk_parent_todo",
        UUID(as_uuid=True),
        ForeignKey("tb_todo.pk_todo"),
    ),
    Column("identifier", String(255), unique=True),
    Column("path", LtreeType),
    Index("ix_todo_path", "path", postgresql_using="gist"),
)


def start_mappers():
    mapper_registry.map_imperatively(
        model.TodoInfo,
        table_todo_info,
    )

    mapper_registry.map_imperatively(
        model.Todo,
        table_todo,
        properties={
            "info": relationship(model.TodoInfo, uselist=False),
            "parent_todo": relationship(model.Todo, remote_side=[table_todo.c.pk_todo]),
        },
    )
