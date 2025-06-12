from fastapi import APIRouter, FastAPI

from .routers.auth_router import router as auth_router
from .routers.user_router import router as user_router

router = APIRouter(prefix='/api/v1')
app = FastAPI()

router.include_router(user_router)

app.include_router(auth_router)

app.include_router(router)
