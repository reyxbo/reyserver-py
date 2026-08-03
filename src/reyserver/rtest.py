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
        'spent_s': float,
        'count_size': int,
        'progress': float,
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
    First receive `{'total_s': float}` setting total seconds, value range is (0-10], loop receive `bytes` and send statistics parameters.
    """

    # Parameter.
    max_size = int(3.125 * 1024 * 1024 * 1024)
    count_size = 0
    max_s = 10
    interval_s = 0.1
    last_total_spend = 0
    tm = TimeMark()

    # Connect.
    await websocket.accept()

    ## Set.
    try:
        setting = await websocket.receive_json()
        total_s = setting['total_s']
    except WebSocketDisconnect:
        return
    if not 0 < total_s <= max_s:
        await websocket.close()
        return

    ## Receive.
    while True:
        try:
            chunk = await websocket.receive_bytes()
        except WebSocketDisconnect:
            break
        count_size += len(chunk)
        del chunk
        tm()
        spent_s = tm.total_spend

        ## Break.
        if (
            spent_s >= total_s
            or count_size >= max_size
        ):
            try:
                await websocket.send_json(
                    {
                        'spent_s': spent_s,
                        'count_size': count_size,
                        'progress': min(spent_s / total_s, 1),
                        'mbps': count_size * 8 / 1_000_000 / spent_s,
                        'done': True
                    }
                )
            except WebSocketDisconnect:
                break
            await websocket.close()
            break

        ## Send.
        if spent_s - last_total_spend >= interval_s:
            try:
                await websocket.send_json(
                    {
                        'spent_s': spent_s,
                        'count_size': count_size,
                        'progress': min(spent_s / total_s, 1),
                        'mbps': count_size * 8 / 1_000_000 / spent_s,
                        'done': False
                    }
                )
            except WebSocketDisconnect:
                break
            last_total_spend = spent_s

@router_test.get('/upload')
async def test_upload_websocket() -> TestUploadReceiveParameters:
    """
    For document only.
    Test upload, websocket connection of receive bytes data. Maximum limit 1 GB and 10 seconds.
    First receive `{'total_s': float}` setting total seconds, value range is (0-10], loop receive `bytes` and send statistics parameters.

    Returns
    -------
    Send statistics parameters.
    """

    # Connot use.
    exit_api(404)

@router_test.get('/download')
async def test_download(
    total_s: float = Bind.Query(5, gt=0, le=10)
) -> StreamingResponse:
    """
    Test download.

    Parameters
    ----------
    total_s : Download seconds, value range is (0-10].

    Returns
    -------
    Bytes data.
    """

    # Parameter.
    each_size = 256 * 1024
    chunk = b'01234567' * int(each_size / 8)

    # Download.
    async def generator():
        tm = TimeMark()
        while True:
            tm()
            if tm.total_spend >= total_s:
                break
            yield chunk
            await async_sleep(0)
    response = StreamingResponse(
        generator(),
        headers={'Cache-Control': 'no-store'}
    )

    return response
