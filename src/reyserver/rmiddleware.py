#!/usr/bin/env python3

"""
@Time    : 2026-08-07
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Middleware module.
    Provides middleware for route and response processing.
"""

from starlette.types import Scope, Receive, Send
from fastapi.middleware.gzip import GZipMiddleware as FGZipMiddleware

from . import rserver

__all__ = (
    'GZipMiddleware',
)

class GZipMiddleware(FGZipMiddleware):
    """
    Re encapsulate GZip middleware of custom filter.
    """

    def __init__(self, *args, server: 'rserver.Server', **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.server = server
        self.default_gzip_skip_paths = (
            f'get {self.server._prefix}/test/download',
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope['type'] != 'http'
            or (match_path := f'{scope.get('method', '')} {scope.get('path', '')}'.lower()) in self.default_gzip_skip_paths
            or match_path in self.server.gzip_skip_paths
        ):
            await self.app(scope, receive, send)
            return
        await super().__call__(scope, receive, send)
