# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026-06-09
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Mapping link methods.
"""

from pydantic import HttpUrl
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from reydb import rorm, DatabaseEngine, DatabaseEngineAsync

from .rbase import ServerBase
from .rbind import Bind
from .rcache import wrap_cache

class ServerORMTableLink(ServerBase, rorm.Table):
    """
    Server mapping link `link` table ORM model.
    """

    __name__ = 'link'
    __comment__ = 'Mapping link table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record update time.')
    expire_time: rorm.Datetime = rorm.Field(index_n=True, comment='Link expire time.')
    id: int = rorm.Field(key_auto=True, comment='ID.')
    url: str = rorm.Field(rorm.types.TEXT, not_null=True, index_u=True, comment='Redirect URL.')
    user_id: int = rorm.Field(index_n=True, comment='Link owner user ID. When is null, then owner is system.')

def build_db_link(engine: DatabaseEngine | DatabaseEngineAsync) -> None:
    """
    Check and build `link` database tables.

    Parameters
    ----------
    db : Database engine instance.
    """

    # Set parameter.

    ## Table.
    tables = [ServerORMTableLink]

    ## View stats.
    views_stats = [
        {
            'table': 'stats_link',
            'items': [
                {
                    'name': 'count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "link"'
                    ),
                    'comment': 'Mapping link count.'
                },
                {
                    'name': 'past_day_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "link"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                    ),
                    'comment': 'Mapping link count in the past day.'
                },
                {
                    'name': 'past_week_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "link"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                    ),
                    'comment': 'Mapping link count in the past week.'
                },
                {
                    'name': 'past_month_count',
                    'select': (
                        'SELECT COUNT(1)\n'
                        'FROM "link"\n'
                        'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                    ),
                    'comment': 'Mapping link count in the past month.'
                },
                {
                    'name': 'last_time',
                    'select': (
                        'SELECT MAX("create_time")\n'
                        'FROM "link"'
                    ),
                    'comment': 'Mapping link last record create time.'
                }
            ]
        }
    ]

    # Build.
    engine.sync_engine.build(tables=tables, views_stats=views_stats, skip=True)

router_link = APIRouter()
router_link_l = APIRouter()

@router_link.get('/')
async def get_links(
    page_params: Bind.PageParams = Bind.page,
    user: Bind.User = Bind.user,
    conn: Bind.Conn = Bind.conn.file,
    sess: Bind.Sess = Bind.sess.link
) -> Bind.Page[ServerORMTableLink]:
    """
    Get mapping link table.

    Returns
    -------
    Page data of mapping link table.
    """

    # Parameter.
    if user.is_admin:
        where = 'TRUE'
    else:
        where = f'"user_id" = {user.user_id}'

    # Get.
    models_file_info = await (
        sess.select(ServerORMTableLink)
        .where(where)
        .order_by('"create_time" DESC')
        .offset(page_params['offset'])
        .limit(page_params['limit'])
        .execute()
    )

    # Total.
    if page_params['with_total']:
        total = await conn.execute.count(ServerORMTableLink, where)
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

@router_link.get('/{code}')
@router_link_l.get('/l/{code}')
@wrap_cache
async def map_link(
    code: str = Bind.i.path,
    sess: Bind.Sess = Bind.sess.file
) -> RedirectResponse:
    """
    Redirect URL by mapping link.
    """

    # Get.
    link_id = decode_link(code)
    model_link = await sess.get(ServerORMTableLink, link_id)

    # Response.
    response = RedirectResponse(model_link.url, 308)

    return response

@router_link.post('/')
async def create_link(
    url: str = Bind.i.body_k,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> ServerORMTableLink: ...

@router_link.delete('/{code}')
async def expire_link(
    code: str = Bind.i.path,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> None: ...

def encode_link(link_id: int) -> str:
    """
    Encode link code to link ID.

    Parameters
    ----------
    code : Link code.

    Returns
    -------
    Link ID.
    """

    ...

def decode_link(code: str) -> int:
    """
    Decode link code to link ID.

    Parameters
    ----------
    link_id : Link ID.

    Returns
    -------
    Link code.
    """

    ...
