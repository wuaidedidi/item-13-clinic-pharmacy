from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "操作成功") -> JSONResponse:
    return JSONResponse(status_code=200, content=jsonable_encoder({"code": 200, "message": message, "data": data}))


def failure(code: int, message: str, data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=jsonable_encoder({"code": code, "message": message, "data": data}))
