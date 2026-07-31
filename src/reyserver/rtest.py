#!/usr/bin/env python3

"""
@Time    : 2025-10-21
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Test methods.
"""

from typing import Literal
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from reykit.rtask import async_sleep
from reykit.rtime import now, TimeMark

from .rbind import Bind
from .rbase import exit_api

__all__ = (
    'router_test',
)

router_test = APIRouter()

@router_test.get('')
async def test() -> Literal['test']:
    """
    Test.

    Returns
    -------
    Text `test`.
    """

    # Resposne.
    response = 'test'

    return response

@router_test.post('/echo')
async def test_echo(data: dict = Bind.i.body) -> dict:
    """
    Echo test.

    Paremeters
    ----------
    data : Echo data.

    Returns
    -------
    Echo data.
    """

    return data

@router_test.get('/wait')
async def test_wait(second: float = Bind.Query(1, gt=0, le=10)) -> Literal['test']:
    """
    Wait test.

    Paremeters
    ----------
    second : Wait seconds, range is `(0-10]`.

    Returns
    -------
    Text `test`.
    """

    # Sleep.
    await async_sleep(second)

    # Resposne.
    response = 'test'

    return response

@router_test.get('/ping')
async def test_ping() -> int:
    """
    Test server time.

    Returns
    -------
    Server time.
    """

    # Sleep.
    timestamp = now('timestamp')

    return timestamp

@router_test.post('/upload')
async def test_upload(
    file: Bind.UploadFile = Bind.Forms()
) -> None:
    """
    Test upload. Maximum limit 1 GB and 10 seconds.

    Parameters
    ----------
    file : File instance.
    """

    # Parameter.
    max_size = 1024 * 1024 * 1024
    each_size = 1024 * 1024
    count_size = 0
    timeout_s = 60
    tm = TimeMark()

    # Upload.
    while True:
        tm()
        if tm.total_spend >= timeout_s:
            exit_api(408)
        data = await file.read(each_size)
        count_size += len(data)
        if count_size >= max_size:
            exit_api(413)

@router_test.get('/download')
async def test_download(
    s: float = Bind.Query(5, gt=0, le=10)
) -> StreamingResponse:
    """
    Test download.

    Parameters
    ----------
    s : Download seconds, value range is (0-10).
    """

    # Parameter.
    each_size = 1024 * 1024
    chunk = b'0' * each_size

    # Download.
    async def generator():
        tm = TimeMark()
        while True:
            tm()
            if tm.total_spend >= s:
                break
            yield chunk
    response = StreamingResponse(generator())

    return response
