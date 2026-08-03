#!/usr/bin/env python3

"""
@Time    : 2025-07-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base methods.
"""

from typing import NoReturn
from http import HTTPStatus
from starlette.types import Scope, Receive, Send
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.middleware.gzip import GZipMiddleware as FGZipMiddleware
from reykit.rbase import Base, Exit, throw
from reydb import rorm

__all__ = (
    'ServerBase',
    'ServerExit',
    'ServerExitAPI',
    'exit_api',
    'depend_pass',
    'GZipMiddleware'
)

class ServerBase(Base):
    """
    Server base type.
    """

class ServerExit(ServerBase, Exit):
    """
    Server exit type.
    """

class ServerExitAPI(ServerExit, HTTPException):
    """
    Server exit API type.
    """

class Page[T](ServerBase, rorm.Model):
    """
    Response of one page data.
    """

    offset: int | None = rorm.Field(num_ge=0)
    "Start offset count."
    limit: int | None = rorm.Field(num_ge=0)
    "End limit count."
    data: list[T]
    "Data table."
    total: int | None
    "Row total count."

def exit_api(code: int = 400, text: str | None = None) -> NoReturn:
    """
    Throw exception to exit API.

    Parameters
    ----------
    code : Response status code.
    text : Explain text.
        `None`: Use Default text.
    """

    # Parameter.
    if not 400 <= code <= 499:
        throw(ValueError, code)
    if text is None:
        status = HTTPStatus(code)
        text = status.description

    # Throw exception.
    raise ServerExitAPI(code, text)

async def depend_pass_func() -> None:
    """
    Depend pass.
    """

depend_pass = Depends(depend_pass_func)

class GZipMiddleware(FGZipMiddleware):
    """
    Re encapsulate GZip middleware of custom filter.
    """

    def __init__(self, *args, filter_paths: list[str], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.filter_paths = filter_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope['type'] != 'http'
            or f'{scope.get('method', '')} {scope.get('path', '')}'.lower() in self.filter_paths
        ):
            await self.app(scope, receive, send)
            return
        await super().__call__(scope, receive, send)
