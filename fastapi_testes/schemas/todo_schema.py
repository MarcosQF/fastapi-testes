from pydantic import BaseModel, Field

from ..models.todo_model import TodoState


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.draft)


class TodoPublic(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoSoftUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None
