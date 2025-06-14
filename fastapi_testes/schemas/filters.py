from pydantic import BaseModel, Field

from fastapi_testes.models.todo_model import TodoState


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=100)


class FilterTodo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=20)
    descripton: str | None = None
    state: TodoState | None = None
