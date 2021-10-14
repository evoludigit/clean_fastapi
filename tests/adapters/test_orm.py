import uuid

from clean.domain import model


# for each object from the domain, we run the following 2 tests
# 1. ADD :
# 1.1 instanciate the object from the model (eg. datasupplier = model.Datasupplier(attrs))
# 1.2 add and commit object to the session : session.add(datasupplier) / session.commit()
# 1.3 assert that the data returned by a raw SQL SELECT is equal to the instanciated data

# 2. QUERY :
# 2.1 insert data using raw SQL INSERT
# 2.2 instanciate the object from the model, with the same data from 2.1
# 2.3 assert that the object returned from session.query is equal to instanciated object


def test_TodoInfo_mapper_can_add(session):
    # instanciation des objets
    note_info = model.TodoInfo(
        name="make crêpes", due_date="today", description="Yummy"
    )
    session.add(note_info)
    session.commit()
    row = list(
        session.execute(
            """
            SELECT
            name,
            due_date,
            description
            FROM tb_todo_info
            """,
        ),
    )[0]
    assert row == ("make crêpes", "today", "Yummy")


def test_TodoInfo_mapper_can_query(session):
    # instanciation des objets
    pk_todo_info = uuid.uuid4()
    todo_info_identifier = "make_pizza"
    name = "make Pizza"
    due_date = "this week-end"
    description = "Please don’t add Pineapple"
    session.execute(
        """
        INSERT INTO tb_todo_info
        (pk_todo_info,
         identifier,
         name,
         due_date,
         description)
        VALUES (
          :pk_todo_info,
          :todo_info_identifier,
          :name,
          :due_date,
          :description
          )
        """,
        {
            "pk_todo_info": pk_todo_info,
            "todo_info_identifier": todo_info_identifier,
            "name": name,
            "due_date": due_date,
            "description": description,
        },
    )
    todo_info = model.TodoInfo(name, due_date, description)
    session.add(todo_info)
    session.commit()
    row = list(
        session.execute(
            """
            SELECT
            name,
            due_date,
            description
            FROM tb_todo_info
            """,
        ),
    )[0]
    assert row == (name, due_date, description)
