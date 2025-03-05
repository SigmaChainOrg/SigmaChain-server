from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    msg: str
    data: T
    ok: bool = False


class APIErrorResponse(BaseModel):
    detail: str | List[str]
    ok: bool = False
