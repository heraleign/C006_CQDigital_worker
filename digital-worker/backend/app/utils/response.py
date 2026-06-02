from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: PaginatedData


def success_response(data: Any = None, message: str = "success") -> ResponseModel:
    return ResponseModel(code=200, message=message, data=data)


def error_response(
    message: str = "error",
    code: int = 400,
    data: Any = None,
) -> ResponseModel:
    return ResponseModel(code=code, message=message, data=data)


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "success",
) -> PaginatedResponse:
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return PaginatedResponse(
        code=200,
        message=message,
        data=PaginatedData(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


def server_error_response(message: str = "Internal server error") -> ResponseModel:
    return ResponseModel(code=500, message=message, data=None)
