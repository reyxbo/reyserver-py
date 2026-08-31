#!/usr/bin/env python3

"""
@Time    : 2026-08-31
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Database methods.
"""

from typing import Any
from fastapi import APIRouter

from .rbase import exit_api
from .rbind import Bind

__all__ = (
    'router_db',
)

router_db = APIRouter()

@router_db.get('/{database_name}/{table_name}', dependencies=(Bind.user,))
async def get_database_table_data(
    database_name: str = Bind.i.path,
    table_name: str = Bind.i.path,
    fields: str | None = Bind.i.query_n,
    where: str | None = Bind.i.query_n,
    group: str | None = Bind.i.query_n,
    having: str | None = Bind.i.query_n,
    order: str | None = Bind.i.query_n,
    limit: int | None = Bind.i.query_n,
    offset: int | None = Bind.i.query_n,
    db: Bind.Database = Bind.database,
    server: Bind.Server = Bind.server
) -> list[dict[str, Any]]:
    """
    Get table data from database, filtered by variable `database_table_allowlist`.

    Parameters
    ----------
    database_name : Database name.
    table_name : Table name.
    fields : Clause `WHERE` content, join as `SELECT str`.
    where : Clause `WHERE` content, join as `WHERE str`.
    group : Clause `GROUP BY` content, join as `GROUP BY str`.
    having : Clause `HAVING` content, join as `HAVING str`.
    order : Clause `ORDER BY` content, join as `ORDER BY str`.
    limit : Clause `LIMIT` content, join as `LIMIT int`.
    offset : Clause `OFFSET` content, join as `OFFSET int`.

    Returns
    -------
    Table data.
    """

    # Check.
    if table_name not in server.database_table_allowlist.get(database_name, []):
        exit_api(404)

    # Select.
    engine = db[database_name]
    result = await engine.execute.select(
        table_name,
        fields,
        where,
        group,
        having,
        order,
        limit,
        offset
    )
    data = result.to_table()

    return data
