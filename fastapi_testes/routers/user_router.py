from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_testes.database import get_session
from fastapi_testes.security import get_current_user, get_password_hash

from ..models.user_model import User
from ..schemas.user_schema import Message, UserList, UserPublic, UserSchema

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    users = session.scalars(select(User).limit(limit).offset(offset))

    return {'users': users}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                detail='Username already exists',
                status_code=HTTPStatus.CONFLICT,
            )
        elif db_user.email == user.email:
            raise HTTPException(
                detail='Email already exists', status_code=HTTPStatus.CONFLICT
            )

    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
