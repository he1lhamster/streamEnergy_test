from fastapi import FastAPI

from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from limiter import limiter
from notes.routers import router as notes_router
from users.routers import router as users_router

app = FastAPI()
app.state.limiter = limiter


@app.on_event("startup")
async def startup_event():
    # запускаем лимитер вместе с запуском приложения
    app.state.limiter = limiter
#     asyncio.create_task(main())


# тестовый хэндлер для проверки доступности сервера
@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(users_router)
app.include_router(notes_router)

app.add_middleware(SlowAPIMiddleware)


# настраиваем ответ пользователю от лимитера
@app.exception_handler(429)
async def rate_limit_exceeded(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

# добавим CORS мидлвару для ограничения доступа со сторонних хостов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)