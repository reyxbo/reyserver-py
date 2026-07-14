# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-10-25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Cache methods.
"""

from typing import Any, overload
from collections.abc import Callable
from functools import wraps
from asyncio import Lock
from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.coder import PickleCoder
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache as fastapi_cache_cache
from redis.asyncio import Redis
from reykit.rbase import CallableT
from reykit.ros import get_md5
from reykit.rre import sub

__all__ = (
    'load_cache_version',
    'init_cache',
    'wrap_cache',
    'get_redis',
    'get_cache_version',
    'expire_cache'
)

_cache_version_dict: dict[str, int] = {}
_cache_version_lock = Lock()

async def load_cache_version(label: str) -> None:
    """
    Loading cache version by label.

    Parameters
    ----------
    label : Cache label.
    """

    # Load.
    if label in _cache_version_dict:
        return
    async with _cache_version_lock:
        if label in _cache_version_dict:
            return
        name = f'version:{label}'
        redis = get_redis()
        version = int(
            await redis.get(name)
            or 1
        )
        _cache_version_dict[label] = version

def init_cache(redis: Redis, redis_expire: int | None = None) -> None:
    """
    Initialize cache based on Redis.

    Parameters
    ----------
    redis : Asynchronous Redis
    redis_expire : Redis cache expire seconds.
    """

    def key_builder(
        func: Callable,
        namespace: str,
        request: Request,
        response: Response,
        args: tuple,
        kwargs: dict[str, Any],
    ) -> str:
        """
        Cache key builder.

        Parameters
        ----------
        func : Decorated function.
        namespace : Cache key prefix.
        request : API Request.
        response : API response.
        args : Position arguments of decorated function.
        kwargs : Keyword arguments of decorated function.
        """

        # Build.
        if func._key is None:
            data = f'{func.__module__}:{func.__name__}:{args}:{kwargs}'
            pattern = r' object at 0x[0-9a-fA-F]+>'
            data = sub(pattern, data, '>')
        else:
            func_key: str | tuple[str] | Callable[[tuple, dict[str, Any]], Any] = func._key
            if callable(func_key):
                data = str(func_key(args, kwargs))
            else:
                if type(func_key) is str:
                    func_key = (func_key,)
                data = ':'.join([
                    f'{name}={kwargs[name]}'
                    for name in func_key
                ])
                pattern = r' object at 0x[0-9a-fA-F]+>'
                data = sub(pattern, data, '>')
        key_label: str = func._key_label
        version = _cache_version_dict.get(key_label, 1)
        data = f'{key_label}:{version}:{data}'
        key = get_md5(data)

        return key

    # Initialize.
    backend = RedisBackend(redis)
    FastAPICache.init(
        backend,
        expire=redis_expire,
        coder=PickleCoder,
        key_builder=key_builder
    )

@overload
def wrap_cache(func: CallableT) -> CallableT: ...

@overload
def wrap_cache(
    *,
    expire: int | None = None,
    key: str | tuple[str] | Callable[[tuple, dict[str, Any]], Any] | None = None,
    key_label: str | None = None
) -> Callable[[CallableT], CallableT]: ...

def wrap_cache(
    func: CallableT | None = None,
    *,
    expire: int | None = None,
    key: str | tuple[str] | Callable[[tuple, dict[str, Any]], Any] | None = None,
    key_label: str | None = None
) -> CallableT | Callable[[CallableT], CallableT]:
    """
    Decorator, use Redis cache.
    When Redis is not set, then skip.

    Parameters
    ----------
    func : Decorated route function.
    expire : Cache expire seconds.
    key : Set cache key from arguments.
        - `str | tuple[str]`: Call keyword argument names of route function, join to cache key.
        - `Callable[[tuple, dict[str, Any]], str]`: Callback function, enter all positional arguments and keyword arguments, return cache key value.
    key_label : Set cache label, used for caching version control.
        - `None`: Use function name.

    Returns
    -------
    Decorated function or decorator.

    Examples
    --------
    No parameter.
    >>> @wrap_cache
    >>> def foo(): ...

    Set parameter.
    >>> @wrap_cache(**kwargs)
    >>> def foo(): ...
    """

    # Decorator.
    def decorator(func):

        # Annotation.
        note_title = 'Notes\n-----'
        cache_note = '\nThe response will based on Redis caching.\n'
        if not func.__doc__:
            func.__doc__ = note_title + cache_note
        if note_title in func.__doc__:
            func.__doc__ = func.__doc__.replace(note_title, note_title + cache_note)
        else:
            func.__doc__ += '\n' + note_title + cache_note

        # Cache.
        func.__cache__ = True
        func._key = key
        func._key_label = key_label or func.__name__

        # Decorate.
        cache_decorator = fastapi_cache_cache(expire=expire)
        cache_func = cache_decorator(func)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await cache_func(*args, **kwargs)
            return result

        return wrapper

    ## Parameter.
    if func is None:
        return lambda func: decorator(func)

    ## Function.
    else:
        return decorator(func)

def get_redis() -> Redis:
    """
    Get redis instance of cache backend.

    Returns
    -------
    Redis instance.
    """

    # Get.
    backend: RedisBackend = FastAPICache.get_backend()
    redis: Redis = backend.redis

    return redis

@overload
async def expire_cache(
    label: str | Callable
) -> None: ...

@overload
async def expire_cache(
    label: str | Callable,
    data: Any
) -> None: ...

@overload
async def expire_cache(
    label: str | Callable,
    **kwargs: Any
) -> None: ...

async def expire_cache(
    label: str | Callable,
    data: Any | None = None,
    **kwargs: Any
) -> None:
    """
    Expire one cache by label.

    Parameters
    ----------
    label : Cache label.
        - `Callable`: Function name.
    data : Cache key value.
    kwargs : Cache keyword arguments, join to cache key.
    """

    # Parameter.
    if callable(label):
        label = label.__name__

    # Expire label.
    if (
        data is None
        and kwargs == {}
    ):
        async with _cache_version_lock:
            _cache_version_dict[label] = _cache_version_dict.get(label, 1) + 1
            name = f'version:{label}'
            redis = get_redis()
            await redis.incrby(name)

    # Expire one key.
    else:
        if data is None:
            data = ':'.join([
                f'{name}={value}'
                for name, value in kwargs.items()
            ])
            async with _cache_version_lock:
                version = _cache_version_dict.get(label, 1)
            pattern = r' object at 0x[0-9a-fA-F]+>'
            data = sub(pattern, data, '>')
        else:
            data = str(data)
        version = _cache_version_dict.get(label, 1)
        data = f'{label}:{version}:{data}'
        key = get_md5(data)
        redis = get_redis()
        await redis.delete(key)
