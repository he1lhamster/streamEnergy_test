import asyncio

from fastapi import FastAPI
from notes.routers import router as notes_router
from users.routers import router as users_router
from tgbot import main

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # Start the Telegram bot in a separate task
    asyncio.create_task(main())


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(users_router)
app.include_router(notes_router)
