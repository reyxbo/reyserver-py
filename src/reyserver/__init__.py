#!/usr/bin/env python3

"""
@Time    : 2023-02-19
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Backend asynchronous server integration API framework built on FastAPI.

Modules
-------
rall : Unified export module.
    Provides convenient exports for all reyserver modules, methods, and objects.
    It allows framework functionality to be imported from a centralized module, reducing the need to import components separately from multiple modules.
rauth : User authentication module.
    Based on the **RBAC (Role-Based Access Control)** model, this module manages access permissions through users, roles, and permissions.
rbase : Base utility module.
    Provides common methods and shared functionality used by other modules.
rbind : Dependency injection module.
    Provides convenient imports for commonly used dependency objects in route functions.
    Through predefined singleton objects, API endpoints can easily access various contexts and resources during server operation.
rcache : Cache module.
    Provides API caching capabilities based on Redis.
rclient : Client module.
    Provides convenient client methods for calling APIs provided by the server.
rdb : Database module.
    Provides convenient methods for creating database APIs.
    By specifying database table names, corresponding data APIs can be created quickly, reducing the amount of repetitive database API code that needs to be written.
rfile : File service module.
    Provides file upload, download, and file management APIs, including streaming downloads.
rlink : Short link module.
    Provides APIs for mapping long URLs to short URLs.
rmiddleware : Middleware module.
    Provides middleware for route and response processing.
rpublic : Public resource module.
    Provides APIs for website homepages, public files, and frontend static resources.
rredirect : Request forwarding module.
    Provides server-wide request proxying and forwarding functionality.
rserver : Top-level server module.
    Provides the top-level server object of reyserver and serves as the primary entry point for using the framework.
rtest : Testing module.
    Provides server health and network performance testing APIs.
"""

from .rserver import Server as Server
