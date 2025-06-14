from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_testes.database import get_session
from fastapi_testes.models.todo_model import Todo
from fastapi_testes.models.user_model import User
from fastapi_testes.schemas.filters import FilterTodo
from fastapi_testes.schemas.todo_schema import (
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoSoftUpdate,
)
from fastapi_testes.schemas.user_schema import Message
from fastapi_testes.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema, user: T_CurrentUser, session: T_Session
):
    db_todo = Todo(
        user_id=user.id,
        title=todo.title,
        description=todo.description,
        state=todo.state,
    )

    session.add(db_todo)

    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(
    session: T_Session,
    user: T_CurrentUser,
    filters: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if filters.title:
        query = query.filter(Todo.title.contains(filters.title))

    if filters.descripton:
        query = query.filter(Todo.description.contains(filters.descripton))

    if filters.state:
        query = query.filter(Todo.state == filters.state)

    todos = await session.scalars(
        (query.limit(filters.limit).offset(filters.offset))
    )

    return {'todos': todos.all()}


@router.delete('/{todo_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_todo(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='task not found'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully'}


@router.put('/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoPublic)
async def soft_update_todo(
    todo_id: int, session: T_Session, user: T_CurrentUser, todo: TodoSoftUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
