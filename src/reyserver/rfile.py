# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-10-06
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : File methods. Can create database used "self.build_db" function.
"""

from typing import Literal
from enum import StrEnum
from fastapi import APIRouter
from fastapi.responses import FileResponse
from reydb import rorm, DatabaseEngine, DatabaseEngineAsync
from reykit.rdata import decode_jwt

from .rbase import ServerBase, exit_api
from .rbind import Bind
from .rcache import wrap_cache

__all__ = (
    'ServerFileVisibleEnum',
    'ServerORMTableFileData',
    'ServerORMTableFileInfo',
    'ServerORMTableAuthPerm',
    'build_db_file',
    'router_file'
)

class ServerFileVisibleEnum(ServerBase, StrEnum):
    """
    Server file visible enumeration type.
    """

    PUBLIC = 'public'
    'Public file, no login required.'
    INTERNAL = 'internal'
    'Internal file, any user can read, administrator can delete.'
    PRIVATE = 'private'
    'Private file, file owner user or administrator can read and delete.'

class ServerORMTableFileData(ServerBase, rorm.Table):
    """
    Server file `data` table ORM model.
    """

    __name__ = 'data'
    __comment__ = 'File data table.'
    md5: str = rorm.Field(rorm.types.CHAR(32), key=True, comment='File MD5.')
    size: int = rorm.Field(not_null=True, comment='File bytes size.')
    path: str = rorm.Field(rorm.types.VARCHAR(4095), not_null=True, comment='File disk storage relative path.')

class ServerORMTableFileInfo(ServerBase, rorm.Table):
    """
    Server file `info` table ORM model.
    """

    __name__ = 'info'
    __comment__ = 'File information table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    file_id: int = rorm.Field(key_auto=True, comment='File ID.')
    user_id: int = rorm.Field(not_null=True, index_n=True, comment='File owner user ID.')
    visible: Literal['public', 'internal', 'private'] = rorm.Field(rorm.ENUM(ServerFileVisibleEnum), not_null=True, index_n=True, comment='File visible type.')
    md5: str = rorm.Field(rorm.types.CHAR(32), key_foreign=(ServerORMTableFileData.__tablename__, 'md5'), not_null=True, index_n=True, comment='File MD5.')
    size: int = rorm.Field(not_null=True, comment='File bytes size.')
    name: str | None = rorm.Field(rorm.types.VARCHAR(260), index_n=True, comment='File name.')
    note: str | None = rorm.Field(rorm.types.VARCHAR(500), comment='File note.')

def build_db_file(engine: DatabaseEngine | DatabaseEngineAsync) -> None:
    """
    Check and build "file" database tables.

    Parameters
    ----------
    db : Database engine instance.
    """

    # Set parameter.

    ## Table.
    tables = [ServerORMTableFileData, ServerORMTableFileInfo]

    ## View.
    views = [
        {
            'table': 'data_info',
            'select': (
                'SELECT "b"."last_time", "a"."md5", "a"."size", "b"."names", "b"."notes"\n'
                'FROM "data" AS "a"\n'
                'LEFT JOIN (\n'
                '    SELECT\n'
                '        "md5",\n'
                '        STRING_AGG(DISTINCT "name", \' | \') AS "names",\n'
                '        STRING_AGG(DISTINCT "note", \' | \') AS "notes",\n'
                '        MAX("create_time") as "last_time"\n'
                '    FROM (\n'
                '        SELECT "create_time", "md5", "name", "note"\n'
                '        FROM "info"\n'
                '        ORDER BY "create_time" DESC\n'
                '    ) AS "INFO"\n'
                '    GROUP BY "md5"\n'
                '    ORDER BY "last_time" DESC\n'
                ') AS "b"\n'
                'ON "a"."md5" = "b"."md5"\n'
                'ORDER BY "last_time" DESC'
            )
        }
    ]

    ## View stats.
    views_stats = [
        {
            'table': 'stats',
            'items': [
                {
                    'name': 'count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "info"'
                    ),
                    'comment': 'File information count.'
                },
                {
                    'name': 'past_day_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "info"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                    ),
                    'comment': 'File information count in the past day.'
                },
                {
                    'name': 'past_week_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "info"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                    ),
                    'comment': 'File information count in the past week.'
                },
                {
                    'name': 'past_month_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "info"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                    ),
                    'comment': 'File information count in the past month.'
                },
                {
                    'name': 'data_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "data"'
                    ),
                    'comment': 'File data unique count.'
                },
                {
                    'name': 'total_size',
                    'select': (
                        'SELECT TO_CHAR(SUM("size"), \'FM999,999,999,999,999\')\n'
                        'FROM "data"'
                    ),
                    'comment': 'File total byte size.'
                },
                {
                    'name': 'avg_size',
                    'select': (
                        'SELECT TO_CHAR(ROUND(AVG("size")), \'FM999,999,999,999,999\')\n'
                        'FROM "data"'
                    ),
                    'comment': 'File average byte size.'
                },
                {
                    'name': 'max_size',
                    'select': (
                        'SELECT TO_CHAR(MAX("size"), \'FM999,999,999,999,999\')\n'
                        'FROM "data"'
                    ),
                    'comment': 'File maximum byte size.'
                },
                {
                    'name': 'last_time',
                    'select': (
                        'SELECT MAX("create_time")\n'
                        'FROM "info"'
                    ),
                    'comment': 'File last record create time.'
                }
            ]
        }
    ]

    # Build.
    engine.sync_engine.build(tables=tables, views=views, views_stats=views_stats, skip=True)

router_file = APIRouter()

@router_file.get('/')
async def get_files(
    page_params: Bind.PageParams = Bind.page,
    user: Bind.UserOpt = Bind.user_opt,
    conn: Bind.Conn = Bind.conn.file,
    sess: Bind.Sess = Bind.sess.file
) -> Bind.Page[ServerORMTableFileInfo]:
    """
    Get file information table.

    Returns
    -------
    Page data of file information table.
    """

    # Parameter.
    if user is None:
        where = '"visible" = \'public\''
    elif user.is_admin:
        where = 'TRUE'
    else:
        where = f'"visible" != \'private\' OR "user_id" = {user.user_id}'

    # Get.
    models_file_info = await (
        sess.select(ServerORMTableFileInfo)
        .offset(page_params['offset'])
        .limit(page_params['limit'])
        .where(where)
        .execute()
    )

    # Total.
    if page_params['with_total']:
        total = await conn.execute.count(ServerORMTableFileInfo)
    else:
        total = None

    # Response.
    page = Bind.Page(
        offset=page_params['offset'],
        limit=page_params['limit'],
        data=models_file_info,
        total=total
    )

    return page

@router_file.get('/{file_id}')
@wrap_cache
async def get_file(
    file_id: int = Bind.i.path,
    user: Bind.UserOpt = Bind.user_opt,
    sess: Bind.Sess = Bind.sess.file
) -> ServerORMTableFileInfo:
    """
    Get file information.

    Parameters
    ----------
    file_id : File ID.

    Returns
    -------
    File information.
    """

    # Get.
    model_info = await sess.get(ServerORMTableFileInfo, file_id)

    # Check.
    if model_info is None:
        exit_api(404)
    if not (
        model_info.visible == 'public'
        or user is not None
        and (
            model_info.visible == 'internal'
            or model_info.visible == 'private'
            and model_info.user_id == user.user_id
            or user.is_admin
        )
    ):
        exit_api(403)

    return model_info

@router_file.post('/')
async def create_file(
    model_file_info: ServerORMTableFileInfo = Bind.file_info
) -> ServerORMTableFileInfo:
    """
    Create file.

    Returns
    -------
    File information.
    """

    return model_file_info

@router_file.delete('/{file_id}', dependencies=(Bind.file_check_delete,))
async def delete_file(
    file_id: int = Bind.i.path,
    sess: Bind.Sess = Bind.sess.file,
    server: Bind.Server = Bind.server
) -> None:
    """
    Delete file information and data.

    Parameters
    ----------
    file_id : File ID.
    """

    # Delete.

    ## Information.
    sql_where = f'"file_id" = {file_id}'
    model_file_info, = await sess.delete(ServerORMTableFileInfo).where(sql_where).execute_return()

    ## Data.
    sql_where = (
        f'"md5" = \'{model_file_info.md5}\'\n'
        '    AND NOT EXISTS (\n'
        '        SELECT TRUE\n'
        f'        FROM "{ServerORMTableFileInfo.__tablename__}"\n'
        f'        WHERE "md5" = \'{model_file_info.md5}\'\n'
        ')'
    )
    await sess.delete(ServerORMTableFileData).where(sql_where).execute()

    ## Storge.
    server.api_file_store.delete(model_file_info.md5)

@router_file.get('/{file_id}/content')
async def get_file_conetnt(
    file_id: int = Bind.i.path,
    user: Bind.UserOpt = Bind.user_opt,
    conn: Bind.Conn = Bind.conn.file,
    server: Bind.Server = Bind.server
) -> FileResponse:
    """
    Get file bytes content.

    Parameters
    ----------
    file_id : File ID.

    Returns
    -------
    File data.
    """

    # Parameter.
    file_store = server.api_file_store

    # Search.
    sql = (
        'SELECT "user_id", "visible", "name", (\n'
        '    SELECT "path"\n'
        '    FROM "data"\n'
        '    WHERE "md5" = "info"."md5"\n'
        '    LIMIT 1\n'
        ') AS "path"\n'
        'FROM "info"\n'
        'WHERE "file_id" = :file_id\n'
        'LIMIT 1'
    )
    result = await conn.execute(sql, file_id=file_id)
    params = result.to_row()

    # Check.
    if params is None:
        exit_api(404)
    if not (
        params['visible'] == 'public'
        or user is not None
        and (
            params['visible'] == 'internal'
            or params['visible'] == 'private'
            and params['user_id'] == user.user_id
            or user.is_admin
        )
    ):
        exit_api(403)

    # Response.
    file_abspath = file_store.get_abspath(params['path'])
    response = FileResponse(file_abspath, filename=params['name'])

    return response

@router_file.get('/{file_id}/sign', dependencies=(Bind.file_check_read,))
async def get_file_sign_url(
    file_id: int = Bind.i.path,
    user: Bind.User = Bind.user,
    server: Bind.Server = Bind.server
) -> FileResponse:
    """
    Get file URL with sign token.

    Parameters
    ----------
    file_id : File ID.

    Returns
    -------
    File download URL with sign token.
    """

    from .rauth import encode_token

    # Token.
    token = encode_token(
        'file',
        server.api_auth_key,
        server.api_file_download_token_seconds,
        user.user_id,
        file_id=file_id
    )

    # Response.
    response = f'{server._prefix}/files/signatures/{token}/content'

    return response

@router_file.get('/signatures/{token}/content')
async def get_sign_file_content(
    token: str = Bind.i.path,
    conn: Bind.Conn = Bind.conn.file,
    server: Bind.Server = Bind.server
) -> FileResponse:
    """
    Get file bytes content by sign token.

    Parameters
    ----------
    token : Sign token.

    Returns
    -------
    File data.
    """

    from .rauth import TokenDataFile

    # Check.
    if not server.is_started_auth:
        exit_api(401)

    # Decode.
    token_data: TokenDataFile | None = decode_jwt(token, server.api_auth_key)

    # Check.
    if (
        token_data is None
        or token_data['type'] != 'file'
    ):
        exit_api(403)

    # Download.
    file_id = token_data['file_id']
    response = await get_file_conetnt(file_id, None, conn, server)

    return response
