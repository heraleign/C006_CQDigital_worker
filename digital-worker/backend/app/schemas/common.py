from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=200, description="每页数量")


class IdSchema(BaseModel):
    id: int


class StatusSchema(BaseModel):
    status: int = Field(default=1, description="状态: 0禁用 1启用")


class TimeRangeSchema(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class BatchIdsSchema(BaseModel):
    ids: list[int]


class KeywordSearch(BaseModel):
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
