from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fastapi_testes.dependences import T_OAuth2Form, T_Session
from fastapi_testes.models.user_model import User
from fastapi_testes.security import create_access_token, verify_password

from ..schemas.auth_schema import Token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=Token)
async def login_for_acess_token(
    session: T_Session,
    form_data: T_OAuth2Form,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password (email)',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
