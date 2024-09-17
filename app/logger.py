from loguru import logger
from fastapi import Request, HTTPException
import sys
from datetime import datetime

from starlette.responses import JSONResponse

from main import app

logger.remove()
logger.add(
    sys.stderr, format="{time} {level} {message}", level="INFO", colorize=True
)
logger.add(
    f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
    rotation="00:00",
    retention="10 days",
    compression="zip"
)


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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc} from {request.url}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.detail} on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
