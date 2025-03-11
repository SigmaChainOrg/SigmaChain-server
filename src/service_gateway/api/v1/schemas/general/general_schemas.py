from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    msg: str
    data: T
    ok: bool = Field(default=False, examples=[True, False])


class APIErrorResponse(BaseModel):
    detail: str | List[str]
    ok: bool = False
