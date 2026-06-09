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

@router_link.get('/links')
async def get_links(
    user: Bind.UserOpt = Bind.user_opt,
    sess: Bind.Sess = Bind.sess.link
) -> Bind.Page[ServerORMTableLink]: ...

@router_link.get('/links/{code}')
@router_link.get('/l/{code}')
@wrap_cache
async def map_link(
    code: str = Bind.i.path,
    sess: Bind.Sess = Bind.sess.file
) -> RedirectResponse: ...

@router_link.post('/links')
async def create_link(
    url: str = Bind.i.body_k,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> ServerORMTableLink: ...

@router_link.delete('/links/{code}')
async def expire_link(
    code: str = Bind.i.path,
    user: Bind.User = Bind.user,
    sess: Bind.Sess = Bind.sess.link
) -> None: ...
