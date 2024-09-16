import asyncio

from fastapi import FastAPI
from loguru import logger
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from notes.routers import router as notes_router
from users.routers import router as users_router
from tgbot import main

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())


@app.get("/")
async def root():
    return {"message": "Hello World"}


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(users_router)
app.include_router(notes_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)