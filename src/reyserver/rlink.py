# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026-06-09
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Mapping link methods.
"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from reydb import rorm, DatabaseEngine, DatabaseEngineAsync
from reykit.rnum import encode_base62, decode_base62
from reykit.rtime import now

from .rbase import ServerBase, throw, exit_api
from .rbind import Bind
from .rcache import wrap_cache, expire_cache

__all__ = (
    'ServerORMTableLink',
    'ServerORMTableLinkOut',
    'build_db_link',
    'router_link',
    'router_link_l'
)

class ServerORMTableLink(ServerBase, rorm.Table):
    """
    Server mapping link `link` table ORM model.
    """

    __name__ = 'link'
    __comment__ = 'Mapping link table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record update time.')
    expire_time: rorm.Datetime | None = rorm.Field(index_n=True, comment='Link expire time.')
    id: int = rorm.Field(key_auto=True, comment='ID.')
    url: str = rorm.Field(rorm.types.TEXT, not_null=True, comment='Redirect HTTP or HTTPS URL.')
    user_id: int = rorm.Field(index_n=True, comment='Link owner user ID. When is null, then owner is system.')

class ServerORMTableLinkOut(ServerBase, rorm.Model):
    """
    Server mapping link out information ORM model.
    """

    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record update time.')
    expire_time: rorm.Datetime | None = rorm.Field(index_n=True, comment='Link expire time.')
    id: int = rorm.Field(key_auto=True, comment='ID.')
    url: str = rorm.Field(rorm.types.TEXT, not_null=True, comment='Redirect HTTP or HTTPS URL.')
    user_id: int = rorm.Field(index_n=True, comment='Link owner user ID. When is null, then owner is system.')
    code: str = rorm.Field(not_null=True, comment='Mapping link code.')

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

@router_link.get('')
async def get_links(
    page_params: Bind.PageParams = Bind.page,
    user: Bind.User = Bind.user,
    conn: Bind.Conn = Bind.conn.link,
    sess: Bind.Sess = Bind.sess.link
) -> Bind.Page[ServerORMTableLinkOut]:
    """
    Get mapping link table.

    Returns
    -------
    Page data of mapping link table.
    """

    # Parameter.
    if user.is_admin:
        where = '"expire_time" IS NULL OR "expire_time" > NOW()'
    else:
        where = f'"user_id" = {user.user_id} AND ("expire_time" IS NULL OR "expire_time" > NOW())'

    # Get.
    models_link = await (
        sess.select(ServerORMTableLink)
        .where(where)
        .order_by('"create_time" DESC')
        .offset(page_params['offset'])
        .limit(page_params['limit'])
        .execute()
    )
    models_link = [
        ServerORMTableLinkOut.r_validate(model, {'code': encode_link(model.id)})
        for model in models_link
    ]

    # Total.
    if page_params['with_total']:
        total = await conn.execute.count(ServerORMTableLink, where)
    else:
        total = None

    # Response.
    page = Bind.Page(
        offset=page_params['offset'],
        limit=page_params['limit'],
        data=models_link,
        total=total
    )

    return page

@router_link.get('/{code}')
@router_link_l.get('/l/{code}')
@wrap_cache(key='code')
async def map_link(
    code: str = Bind.i.path,
    sess: Bind.Sess = Bind.sess.link
) -> RedirectResponse:
    """
    Redirect URL by mapping link.

    Parameters
    ----------
    code : Mapping link code.

    Returns
    -------
    Redirect response.
    """

    # Get.
    link_id = decode_link(code)
    where = f'"id" = {link_id} AND ("expire_time" IS NULL OR "expire_time" > NOW())'
    model_links = (
        await sess.select(ServerORMTableLink)
        .where(where)
        .limit(1)
        .execute()
    )

    # Check.
    if model_links == []:
        exit_api(404)

    # Response.
    model_link, = model_links
    response = RedirectResponse(model_link.url, 308)

    return response

@router_link.post('')
async def create_link(
    url: Bind.HttpUrl = Bind.i.body,
    expire_time: Bind.Datetime | None = Bind.i.body_n,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> ServerORMTableLinkOut:
    """
    Create mapping link.

    Parameters
    ----------
    url : Redirect URL.
    expire_time : Link expire time.

    Returns
    -------
    Link information.
    """

    # Insert.
    data = {
        'expire_time': expire_time,
        'url': str(url),
        'user_id': user.user_id
    }
    model_link, = await (
        sess.insert(ServerORMTableLink)
        .values(data)
        .execute_return()
    )

    # Response.
    model_link_out = ServerORMTableLinkOut.r_validate(model_link, {'code': encode_link(model_link.id)})

    return model_link_out

@router_link.delete('/{link_id}')
async def expire_link(
    link_id: int = Bind.i.path,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> None:
    """
    Expire mapping link.

    Parameters
    ----------
    link_id : Link ID.
    """

    # Update.
    where = f'"id" = {link_id} AND "user_id" = {user.user_id} AND ("expire_time" IS NULL OR "expire_time" > NOW())'
    result = await (
        sess.update(ServerORMTableLink)
        .values(expire_time=now())
        .where(where)
        .execute()
    )

    # Check.
    if result.empty:
        exit_api(404)

    # Cache.
    code = encode_link(link_id)
    await expire_cache(map_link, code=code)

def encode_link(link_id: int) -> str:
    """
    Encode link ID to link code.

    Parameters
    ----------
    code : Link code.

    Returns
    -------
    Link code.
    """

    # Check.
    if link_id < 1:
        throw(ValueError, link_id)

    # Encode.
    code = encode_base62(link_id).rjust(4, '0')

    return code

def decode_link(code: str) -> int:
    """
    Decode link code to link ID.

    Parameters
    ----------
    link_id : Link code.

    Returns
    -------
    Link ID.
    """

    # Decode.
    link_id = decode_base62(code)

    # Check.
    if link_id == 0:
        throw(ValueError, link_id)

    return link_id
