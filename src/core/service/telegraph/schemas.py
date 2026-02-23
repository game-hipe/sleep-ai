from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, HttpUrl, Field

_T = TypeVar("_T")


class BaseResponse(BaseModel, Generic[_T]):
    ok: bool
    result: Optional[_T] = Field(default=None)


class ErrorResponse(BaseResponse[None]):
    error: str


class Node(BaseModel):
    tag: str
    attrs: Optional[dict[str, str]]
    children: Optional[list["Node"] | list[str]]


class Account(BaseModel):
    short_name: str
    author_name: str
    author_url: str
    access_token: str
    auth_url: str


class Page(BaseModel):
    path: str
    url: HttpUrl
    title: str
    description: str | None = Field(default=None)
    author_name: str | None = Field(default=None)
    author_url: str | None = Field(default=None)
    image_url: HttpUrl | None = Field(default=None)
    content: list["Node"] | None = Field(default=None)
    views: int = Field(default=0)
    can_edit: bool = Field(default=False)


class AccountResponse(BaseResponse[Account]): ...


class PageResponse(BaseResponse[Page]): ...
