from cleanarchitecture_fastapi.domain import model

def test_todo_can_generate_identifier():
    todo_info = model.TodoInfo(
        name="Crêpes party",
        due_date="today",
        description="Let’s make some crêpes"
    )
    my_todo = model.Todo(info=todo_info, parent_todo=None)
    assert my_todo.identifier == "crepes_party"
