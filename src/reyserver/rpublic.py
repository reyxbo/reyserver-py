#!/usr/bin/env python3

"""
@Time    : 2025-10-21
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Public resource module.
    Provides APIs for website homepages, public files, and frontend static resources.
"""

from collections.abc import Sequence
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from reykit.ros import File, Folder

from .rbind import Bind

__all__ = (
    'router_public',
    'add_frontend_route'
)

router_public = APIRouter()

@router_public.get('/')
async def home(server: Bind.Server = Bind.server) -> HTMLResponse:
    """
    Home page.

    Returns
    -------
    Home page HTML content.
    """

    # Parameter.
    public_dir = server.api_public_dir
    file_path = Folder(public_dir) + 'index.html'
    file = File(file_path)

    # Response.
    response = HTMLResponse(file.str)

    return response

@router_public.get('/public/{path:path}')
async def download_public_file(path: str = Bind.i.path) -> FileResponse:
    """
    Download public file.

    Parameters
    ----------
    path : Relative path of based on public directory.

    Returns
    -------
    File.
    """

def add_frontend_route(paths: Sequence[str]) -> None:
    """
    Add and map frontend static route.

    Parameters
    ----------
    paths : Route path.
    """

    # Add.
    for path in paths:
        @router_public.get(path, include_in_schema=False)
        async def mapping_frontend_route(
            server: Bind.Server = Bind.server
        ) -> HTMLResponse:
            """
            Mapping frontend static route.

            Parameters
            ----------
            path : Route path.

            Returns
            -------
            Home page HTML content.
            """

            # Parameter.
            public_dir = server.api_public_dir
            file_path = Folder(public_dir) + 'index.html'
            file = File(file_path)

            # Response.
            response = HTMLResponse(file.str)

            return response
