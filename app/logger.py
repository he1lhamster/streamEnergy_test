import os
from loguru import logger
from fastapi import Request, HTTPException
import sys
from datetime import datetime
from starlette.responses import JSONResponse
from main import app

"""
настраиваем логгер для вывода в консоль и для сохранения файлов в папку logs
логи будут обновляться раз в день в 00:00, срок хранения 10 дней
"""

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.remove()
logger.add(
    sys.stderr, format="{time} {level} {message}", level="INFO", colorize=True
)
logger.add(
    f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log",
    rotation="00:00",
    retention="10 days",
    compression="zip"
)


# логгер будет работать на уровне мидлвары
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error during request: {request.method} {request.url} - {e}")
        raise


# перехватываем ошибки сервера с кодом 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc} from {request.url}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."}
    )


# перехватываем остальные ошибки с другими HTTP кодами и отдаем детали в ответе
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.detail} on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
