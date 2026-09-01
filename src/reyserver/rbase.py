#!/usr/bin/env python3

"""
@Time    : 2025-07-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base utility module.
    Provides common methods and shared functionality used by other modules.
"""

from typing import Any, TypedDict, NoReturn, overload
from http import HTTPStatus
from fastapi import HTTPException
from fastapi.params import Depends
from reydb import rorm, DatabaseEngineAsync
from reykit.rbase import Base, Exit, throw

__all__ = (
    'ServerBase',
    'ServerExit',
    'ServerExitAPI',
    'Page',
    'get_page',
    'exit_api',
    'depend_pass'
)

PageParams = TypedDict('PageParams', {'offset': int | None, 'limit': int | None, 'with_total': bool})
'Page control parameters.'

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

@overload
async def get_page[T: rorm.Table](
    table: T,
    page_params: PageParams,
    conn: DatabaseEngineAsync,
    **kwargs: Any
) -> Page[T]: ...

@overload
async def get_page(
    table: str,
    page_params: PageParams,
    conn: DatabaseEngineAsync,
    **kwargs: Any
) -> Page[dict[str, Any]]: ...

async def get_page[T: rorm.Table](
    table: T | str,
    page_params: PageParams,
    conn: DatabaseEngineAsync,
    **kwargs: Any
) -> Page[T | dict[str, Any]]:
    """
    Asynchronous get response of one page data.

    Parameters
    ----------
    table : Database table.
        - `rorm.Table`: Database table ORM model.
        - `str`: Database table name.
    page_params : Page control parameters.
    conn : Asynchronous database engine.
    kwargs : Database table select keyword arguments.

    Returns
    -------
    Response of one page data.
    """

    # Get.
    result = await conn.execute.select(
        table,
        limit=page_params['limit'],
        offset=page_params['offset'],
        **kwargs
    )
    data = result.to_table()

    # Total.
    if page_params['with_total']:
        total = await conn.execute.count(table)
    else:
        total = None

    # Response.
    page = Page(
        offset=page_params['offset'],
        limit=page_params['limit'],
        data=data,
        total=total
    )

    return page

def exit_api(code: int = 400, text: str | None = None) -> NoReturn:
    """
    Throw exception to exit API.

    Parameters
    ----------
    code : Response status code.
    text : Explain text.
        - `None`: Use Default text.
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
