import tempfile

import pytest
from clean.adapters.orm import metadata
from clean.adapters.orm import start_mappers
from pytest_postgresql import factories
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import clear_mappers
from sqlalchemy.orm import sessionmaker

socket_dir = tempfile.TemporaryDirectory()
postgresql_my_proc = factories.postgresql_proc(  # pylint:disable=W0612
    port=None,
    unixsocketdir=socket_dir.name,
)
postgresql_my = factories.postgresql("postgresql_my_proc")


@pytest.fixture
def in_memory_db(postgresql_my):
    def db_creator():
        return postgresql_my.cursor().connection

    engine = create_engine(
        "postgresql+psycopg2://",
        creator=db_creator,
        pool_pre_ping=True,
    )
    engine.execute(
        text("CREATE EXTENSION IF NOT EXISTS ltree;").execution_options(
            autocommit=True,
        ),
    )
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    clear_mappers()
    start_mappers()
    Session = sessionmaker(bind=in_memory_db)
    session = Session()
    yield session
