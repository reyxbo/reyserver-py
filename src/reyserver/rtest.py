#!/usr/bin/env python3

"""
@Time    : 2025-10-21
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Test methods.
"""

from typing import TypedDict, Literal
from fastapi import APIRouter, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from reykit.rtask import async_sleep
from reykit.rtime import TimeMark

from .rbase import exit_api
from .rbind import Bind

__all__ = (
    'router_test',
)

TestUploadReceiveParameters = TypedDict(
    'TestUploadSend',
    {
        'count_size': int,
        'mbps': float,
        'done': bool
    }
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

@router_test.get('/ip')
async def test_ip(
    request: Bind.Request
) -> str:
    """
    Test IP address of client.

    Returns
    -------
    IP address of client.
    """

    # Get.
    ip = request.client.host

    return ip

@router_test.websocket('/upload')
async def test_upload(
    websocket: Bind.WebSocket
) -> None:
    """
    Test upload, websocket connection of receive bytes data. Maximum limit 3.125 GB and 10 seconds.
    """

    # Parameter.
    max_size = int(3.125 * 1024 * 1024 * 1024)
    count_size = 0
    timeout_s = 10
    interval_s = 0.1
    last_total_spend = 0
    tm = TimeMark()

    # Upload.
    await websocket.accept()
    while True:

        ## Receive.
        try:
            chunk = await websocket.receive_bytes()
        except WebSocketDisconnect:
            break
        count_size += len(chunk)
        del chunk
        tm()
        total_spend = tm.total_spend

        ## Break.
        if (
            total_spend >= timeout_s
            or count_size >= max_size
        ):
            try:
                await websocket.send_json(
                    {
                        'count_size': count_size,
                        'mbps': count_size * 8 / 1_000_000 / total_spend,
                        'done': True
                    }
                )
            except WebSocketDisconnect:
                break
            await websocket.close()
            break

        ## Send.
        if total_spend - last_total_spend >= interval_s:
            try:
                await websocket.send_json(
                    {
                        'count_size': count_size,
                        'mbps': count_size * 8 / 1_000_000 / total_spend,
                        'done': False
                    }
                )
            except WebSocketDisconnect:
                break
            last_total_spend = total_spend

@router_test.get("/upload")
async def test_upload_websocket() -> TestUploadReceiveParameters:
    """
    For document only.
    Test upload, websocket connection of receive bytes data. Maximum limit 1 GB and 10 seconds.

    Parameters
    ----------
    receive : Byets data.

    Returns
    -------
    Send test upload receive statistics parameters.
    """

    # Connot use.
    exit_api(404)

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
