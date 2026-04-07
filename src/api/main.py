import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.routes import router
from src.config.serving import load_serving_config


@asynccontextmanager
async def _lifespan(app: FastAPI):
    cfg = load_serving_config()
    level = getattr(logging, cfg.log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s %(message)s",
        force=True,
    )
    yield


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response


app = FastAPI(
    title="Ethiopian Airlines CV Similarity API",
    version="1.0.0",
    lifespan=_lifespan,
)
app.add_middleware(RequestIdMiddleware)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail),
            "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request payload",
            "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        },
    )
