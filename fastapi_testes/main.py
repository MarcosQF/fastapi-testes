from fastapi import APIRouter, FastAPI

from .routers.user_router import router as user_router

router = APIRouter(prefix='/api/v1')
app = FastAPI()

router.include_router(user_router)

app.include_router(router)
