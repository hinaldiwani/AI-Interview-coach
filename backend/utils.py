import json
from typing import Any
from fastapi.responses import JSONResponse

def success_response(data: Any, message: str = "Success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"status": "success", "message": message, "data": data}
    )

def error_response(message: str = "An error occurred", status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message}
    )
