from typing import Generic, NamedTuple, TypeVar

T = TypeVar("T")


class ResponseMessage(NamedTuple):
    msg: str
    ok: bool


class ResponseData(NamedTuple, Generic[T]):
    data: T
    ok: bool


class ResponseComplete(NamedTuple, Generic[T]):
    msg: str
    data: T
    ok: bool
