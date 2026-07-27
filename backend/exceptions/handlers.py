from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ):
        logger.warning(
            f"{request.method} {request.url.path} | "
            f"{exc.status_code} | {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.detail
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        logger.warning(
            f"Validation Error | {request.method} "
            f"{request.url.path}"
        )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status_code": 422,
                "message": "Validation Error",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception
    ):
        logger.exception(
            f"Unhandled Exception | "
            f"{request.method} {request.url.path}"
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Internal Server Error"
            }
        )