from fastapi import APIRouter, FastAPI

from .routers import auth_router, user_router

router = APIRouter(prefix='/api/v1')
app = FastAPI()

router.include_router(user_router.router)

app.include_router(auth_router.router)

app.include_router(router)
