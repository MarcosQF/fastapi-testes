from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Select
from sqlalchemy.orm import Session

from fastapi_testes.database import get_session
from fastapi_testes.models.user_model import User
from fastapi_testes.security import create_access_token, verify_password

from ..schemas.auth_schema import Token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(Select(User).where(User.email == form_data.username))

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
