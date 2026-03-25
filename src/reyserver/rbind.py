# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-10-21
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Dependency bind methods.
"""

from typing import Literal, overload, TYPE_CHECKING
from pydantic import EmailStr
from fastapi import FastAPI, Request, UploadFile
from fastapi.params import (
    Depends,
    Path,
    Query,
    Header,
    Cookie,
    Body,
    Form,
    File as Forms
)
from fastapi.security import OAuth2PasswordBearer
from reydb.rconn import DatabaseConnectionAsync
from reydb.rorm import DatabaseORMSessionAsync
from reykit.rbase import StaticMeta, Singleton, throw
from reykit.rdata import decode_jwt
from reykit.ros import get_md5
from reykit.rre import search_batch

from .rbase import ServerBase, exit_api

if TYPE_CHECKING:
    from .rauth import TokenDataUser, Token
    from .rfile import ServerFileVisibleEnum, ServerORMTableFileData, ServerORMTableFileInfo
    from .rserver import Server
    type FileModels = tuple[ServerORMTableFileData, ServerORMTableFileInfo]

__all__ = (
    'ServerBindInstanceDatabaseSuper',
    'ServerBindInstanceDatabaseConnection',
    'ServerBindInstanceDatabaseSession',
    'ServerBindInstance',
    'ServerBind',
    'Bind'
)

class ServerBindInstanceDatabaseSuper(ServerBase):
    """
    Server API bind parameter build database instance super type.
    """

    def __getattr__(self, name: str) -> Depends:
        """
        Create dependencie instance of asynchronous database.

        Parameters
        ----------
        name : Database engine name.
        mode : Mode.
            - `Literl['sess']`: Create ORM session instance.
            - `Literl['conn']`: Create connection instance.

        Returns
        -------
        Dependencie instance.
        """

        async def depend_func(request: Request):
            """
            Dependencie function of asynchronous database.
            """

            # Parameter.
            app: FastAPI = request.app
            server: Server = app.extra['server']

            ## Check.
            if server.db is None:
                throw(TypeError, server.db)

            engine = server.db[name]

            # Context.
            match self:
                case ServerBindInstanceDatabaseConnection():
                    async with engine.connect() as conn:
                        yield conn
                case ServerBindInstanceDatabaseSession():
                    async with engine.orm.session() as sess:
                        yield sess

        # Create.
        depend = Depends(depend_func)

        return depend

    @overload
    def __getitem__(self, engine: str) -> DatabaseConnectionAsync: ...

    __getitem__ = __getattr__

class ServerBindInstanceDatabaseConnection(ServerBindInstanceDatabaseSuper, Singleton):
    """
    Server API bind parameter build database connection instance type, singleton mode.
    """

class ServerBindInstanceDatabaseSession(ServerBindInstanceDatabaseSuper, Singleton):
    """
    Server API bind parameter build database session instance type, singleton mode.
    """

class ServerBindInstance(ServerBase, Singleton):
    """
    Server API bind parameter build instance type.
    """

    @property
    def path(self) -> Path:
        """
        Path instance.
        """

        # Build.
        path = Path()

        return path

    @property
    def query(self) -> Query:
        """
        Query instance.
        """

        # Build.
        query = Query()

        return query

    @property
    def query_n(self) -> Query:
        """
        Query instance, default `None`.
        """

        # Build.
        query = Query(None)

        return query

    @property
    def header(self) -> Header:
        """
        Header instance.
        """

        # Build.
        header = Header()

        return header

    @property
    def header_n(self) -> Header:
        """
        Header instance, default `None`.
        """

        # Build.
        header = Header(None)

        return header

    @property
    def cookie(self) -> Cookie:
        """
        Cookie instance.
        """

        # Build.
        cookie = Cookie()

        return cookie

    @property
    def cookie_n(self) -> Cookie:
        """
        Cookie instance, default `None`.
        """

        # Build.
        cookie = Cookie(None)

        return cookie

    @property
    def body(self) -> Body:
        """
        Body instance.
        """

        # Build.
        body = Body()

        return body

    @property
    def body_n(self) -> Body:
        """
        Body instance, default `None`.
        """

        # Build.
        body = Body(None)

        return body

    @property
    def body_k(self) -> Body:
        """
        Body instance of parameter `embed` is `True`.
        """

        # Build.
        body = Body(embed=True)

        return body

    @property
    def body_kn(self) -> Body:
        """
        Body instance of parameter `embed` is `True`, default `None`.
        """

        # Build.
        body = Body(None, embed=True)

        return body

    @property
    def form(self) -> Form:
        """
        Form instance.
        """

        # Build.
        form = Form()

        return form

    @property
    def form_n(self) -> Form:
        """
        Form instance, default `None`.
        """

        # Build.
        form = Form(None)

        return form

    @property
    def forms(self) -> Forms:
        """
        Forms instance.
        """

        # Build.
        forms = Forms()

        return forms

    @property
    def forms_n(self) -> Forms:
        """
        Forms instance, default `None`.
        """

        # Build.
        forms = Forms(None)

        return forms

async def depend_server(request: Request) -> 'Server':
    """
    Dependencie function of now Server instance.

    Returns
    -------
    Server.
    """

    # Get.
    app: FastAPI = request.app
    server: Server = app.extra['server']

    return server

bearer = OAuth2PasswordBearer(
    tokenUrl='/api/auth/token',
    scheme_name='OAuth2Password',
    description='Authentication of OAuth2 password model.',
    auto_error=False
)

class User(ServerBase):
    """
    User data type.
    """

    def __init__(self, token_data: 'TokenDataUser') -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        token_data : Token data.
        """

        # Build.
        self.user_id = int(token_data['sub'])
        self.is_admin = token_data['is_admin']

async def depend_user_opt(
    request: Request,
    server: 'Server' = Depends(depend_server),
    token: 'Token | None' = Depends(bearer)
) -> User | None:
    """
    Dependencie function of user data instance or null.
    If the authentication is not enabled, then throw exception.
    If the no token, then return `None`.
    If the verification fails, then response status code is 401 or 403.

    Returns
    -------
    User instance or `None`.
    """

    # Check.
    if not server.is_started_auth:
        throw(AssertionError, server.is_started_auth)
    if token is None:
        return

    # Parameter.
    key = server.api_auth_key
    api_path = f'{request.method} {request.url.path}'

    # Cache.
    token_data: TokenDataUser | None = getattr(request.state, 'token_data', None)

    # Decode.
    if token_data is None:
        token_data: TokenDataUser | None = decode_jwt(token, key)
        if token_data is None:
            exit_api(401)
        request.state['token_data'] = token_data

    # Authentication.
    if token_data['type'] != 'user':
        exit_api(403)
    perm_apis = [
        f'^{pattern}'
        for pattern in token_data['perm_apis']
    ]
    result = search_batch(api_path, *perm_apis)
    if result is None:
        exit_api(403)

    # Instance.
    user = User(token_data)

    return user

async def depend_user(
    user: User | None = Depends(depend_user_opt)
) -> User:
    """
    Dependencie function of user data instance.
    If the authentication is not enabled, then throw exception.
    If the no token, then response status code is 401.
    If the verification fails, then response status code is 401 or 403.

    Returns
    -------
    User instance.
    """

    # Check.
    if user is None:
        exit_api(401)

    return user

async def depend_file(
    file: UploadFile = Forms(),
    visible: Literal['public', 'internal', 'private'] = Forms(),
    name: str | None = Forms(None),
    note: str | None = Forms(None),
    user: User = Depends(depend_user),
    sess: DatabaseORMSessionAsync = ServerBindInstanceDatabaseSession().file,
    server: 'Server' = Depends(depend_server)
) -> 'FileModels':
    """
    Dependencie function of upload file data and information.

    Parameters
    ----------
    file : File instance.
    visible : File visible type.
    name : File name.
        - `None`: Use `file.filename`.
    note : File note.

    Returns
    -------
    File data and information.
    """

    from .rfile import ServerORMTableFileInfo, ServerORMTableFileData

    # Parameter.
    file_store = server.api_file_store
    file_bytes = await file.read()
    file_md5 = get_md5(file_bytes)
    file_size = len(file_bytes)
    if name is None:
        name = file.filename

    # Upload.
    file_path = file_store.index(file_md5)

    ## Data.
    if file_path is None:
        file_path = file_store.store(file_bytes)
        file_relpath = file_store.get_relpath(file_path)
        model_data = ServerORMTableFileData(
            md5=file_md5,
            size=file_size,
            path=file_relpath
        )
        await sess.add(model_data)
    else:
        model_data = await sess.get(ServerORMTableFileData, file_md5)

    ## Information.
    model_info = ServerORMTableFileInfo(
        user_id=user.user_id,
        visible=visible,
        md5=file_md5,
        name=name,
        note=note
    )
    await sess.add(model_info)

    # Get ID.
    await sess.flush()

    return model_data, model_info

async def depend_file_data(
    file = Depends(depend_file)
) -> 'ServerORMTableFileData':
    """
    Dependencie function of upload file data.

    Returns
    -------
    File data.
    """

    # Parameter.
    file_data, _ = file

    return file_data

async def depend_file_info(
    file = Depends(depend_file)
) -> 'ServerORMTableFileInfo':
    """
    Dependencie function of upload file information.

    Returns
    -------
    File information.
    """

    # Parameter.
    _, file_info = file

    return file_info

async def depend_file_check_visible(
    file_id: int = Path(),
    user: User | None = Depends(depend_user_opt),
    conn: DatabaseConnectionAsync = ServerBindInstanceDatabaseConnection().file
) -> None:
    """
    Dependencie function of check file visible and permission, when it fails, then throw exception to exit API.

    Parameters
    ----------
    file_id : File ID.
    """

    # Select.
    sql = (
        'SELECT "user_id", "visible"\n'
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

class ServerBind(ServerBase, metaclass=StaticMeta):
    """
    Server API bind parameter type.
    """

    Request = Request
    'Reqeust instance dependency type.'
    Path = Path
    'URL source path dependency type.'
    Query = Query
    'URL query parameter dependency type.'
    Header = Header
    'Request header parameter dependency type.'
    Cookie = Cookie
    'Request header cookie parameter dependency type.'
    Body = Body
    'Request body JSON parameter dependency type.'
    Form = Form
    'Request body form parameter dependency type.'
    Forms = Forms
    'Request body multiple forms parameter dependency type.'
    UploadFile = UploadFile
    'Type hints upload file type.'
    Depend = Depends
    'Dependency type.'
    Email= EmailStr
    Conn = DatabaseConnectionAsync
    Sess = DatabaseORMSessionAsync
    i = ServerBindInstance()
    'Server API bind parameter build instance.'
    conn = ServerBindInstanceDatabaseConnection()
    'Server API bind parameter asynchronous database connection.'
    sess = ServerBindInstanceDatabaseSession()
    'Server API bind parameter asynchronous database session.'
    server = Depend(depend_server)
    'Server global instance dependency type.'
    user_opt = Depend(depend_user_opt)
    'Optional current session user data instance dependency type.'
    user = Depend(depend_user)
    'Current session user data instance dependency type.'
    file = Depend(depend_file)
    'Upload file data and information dependency type.'
    file_data = Depend(depend_file_data)
    'Upload file data dependency type.'
    file_info = Depend(depend_file_info)
    'Upload file information dependency type.'
    file_check_visible = Depend(depend_file_check_visible)
    'Check file visible and permission dependency type.'
    User = User
    UserOpt = User | None
    if TYPE_CHECKING:
        Server = Server
        FileModelInfo = ServerORMTableFileInfo
        FileModelData = ServerORMTableFileData
        FileModels = FileModels
    else:
        Server = None
        FileModelInfo = None
        FileModelData = None
        FileModels = None

Bind = ServerBind
