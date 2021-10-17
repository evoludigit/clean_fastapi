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
    todo_info = model.TodoInfo(
        name="make crêpes", due_date="today", description="Yummy"
    )
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
    assert row == ("make crêpes", "today", "Yummy")


def test_TodoInfo_mapper_can_query(session):
    # insert objects
    pk_todo_info = uuid.uuid4()
    name = "make Pizza"
    due_date = "this week-end"
    description = "Please don’t add Pineapple"
    # expected result
    session.execute(
        """
        INSERT INTO tb_todo_info(
            pk_todo_info,
            identifier,
            name,
            due_date,
            description
        )
        VALUES(
            :pk_todo_info,
            :identifier,
            :name,
            :due_date,
            :description
        )
        """,
        {
            "pk_todo_info": pk_todo_info,
            "identifier": model.identifier_from_string(name),
            "name": name,
            "due_date": due_date,
            "description": description,
        },
    )
    expected = model.TodoInfo(name, due_date, description)
    result = session.query(model.TodoInfo).first()
    assert result == expected


def test_Todo_mapper_can_add(session):
    # instanciation des objets
    parent_todo_info = model.TodoInfo(
        name="make crêpes", due_date="today", description="Yummy"
    )
    parent_todo = model.Todo(info=parent_todo_info, parent_todo=None)
    child_todo_info = model.TodoInfo(
        name="buy Sugar", due_date="today", description="brown sugar please"
    )
    child_todo = model.Todo(info=child_todo_info, parent_todo=parent_todo)
    session.add_all([parent_todo_info, child_todo_info, parent_todo, child_todo])
    session.commit()
    ls_identifier = sorted(
        [
            r[0]
            for r in list(
                session.execute(
                    """
            SELECT
            identifier
            FROM tb_todo
            """
                ),
            )
        ]
    )
    assert ls_identifier == ["make_crepes", "make_crepes.buy_sugar"]


def test_hierarchical_todo_mapper_can_query(session):
    # instanciation des objets
    pk_parent_todo_info = uuid.uuid4()
    pk_parent_todo = uuid.uuid4()
    parent_name = "build airplane"
    parent_due_date = "next week-end"
    parent_description = "Please make it sustainable"
    pk_child_todo_info = uuid.uuid4()
    pk_child_todo = uuid.uuid4()
    child_name = "invent electric motor"
    child_due_date = "next friday"
    child_description = "it can be slow"
    # parent_todo_info
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
            "pk_todo_info": pk_parent_todo_info,
            "todo_info_identifier": model.identifier_from_string(parent_name),
            "name": parent_name,
            "due_date": parent_due_date,
            "description": parent_description,
        },
    )
    # parent_todo
    session.execute(
        """
        INSERT INTO tb_todo
        (pk_todo,
         fk_todo_info,
         identifier
        )
        VALUES (
          :pk_todo,
          :fk_todo_info,
          :identifier
          )
        """,
        {
            "pk_todo": pk_parent_todo,
            "fk_todo_info": pk_parent_todo_info,
            "identifier": model.identifier_from_string(parent_name),
        },
    )
    # child_todo_info
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
            "pk_todo_info": pk_child_todo_info,
            "todo_info_identifier": model.identifier_from_string(child_name),
            "name": child_name,
            "due_date": child_due_date,
            "description": child_description,
        },
    )
    # child_todo
    session.execute(
        """
        INSERT INTO tb_todo
        (pk_todo,
         fk_todo_info,
         fk_parent_todo,
         identifier
        )
        VALUES (
          :pk_todo,
          :fk_todo_info,
          :fk_parent_todo,
          :identifier
          )
        """,
        {
            "pk_todo": pk_child_todo,
            "fk_todo_info": pk_child_todo_info,
            "fk_parent_todo": pk_parent_todo,
            "identifier": ".".join(
                [
                    model.identifier_from_string(parent_name),
                    model.identifier_from_string(child_name),
                ]
            ),
        },
    )
    # expected objects
    parent_todo_info = model.TodoInfo(parent_name, parent_due_date, parent_description)
    parent_todo = model.Todo(parent_todo_info, None)
    child_todo_info = model.TodoInfo(child_name, child_due_date, child_description)
    child_todo = model.Todo(info=child_todo_info, parent_todo=parent_todo)
    # run query
    ls_todo = session.query(model.Todo).all()
    assert ls_todo == [parent_todo, child_todo]
