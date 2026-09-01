[中文](README_zh.md)

# reyserver

**reyserver** is a backend asynchronous server integration API framework built on [FastAPI](https://fastapi.tiangolo.com/).

It provides commonly used backend service capabilities, including authentication, database, caching, file management, short links, request forwarding, middleware, and static resources. Through a unified server object and dependency injection mechanism, it simplifies the development of backend API services.

The framework generally follows the **RESTful** style and is suitable for building asynchronous Web APIs and backend services.

## Features

* Asynchronous API framework based on FastAPI
* Follows RESTful API design principles
* Modular design with flexible feature composition
* Provides a unified server object and startup mechanism
* Supports RBAC-based user authentication and permission management
* Supports `HTTPBearer` and `OAuth2PasswordBearer`
* Provides user session state management
* Supports databases and ORM
* Provides Redis-based API caching
* Provides file upload, download, and streaming download
* Supports public, internal, and user-private file visibility
* Provides temporary signed URLs for file downloads
* Provides long URL to short URL conversion
* Provides server-side request proxying and forwarding
* Provides GZIP response compression and filtering middleware
* Provides frontend static resources and public file serving
* Provides server health checks and upload/download speed testing APIs
* Provides commonly used dependency injection objects and parameter validation utilities

---

## Installation

Requires **Python 3.12 or higher**.

```bash
pip install reyserver
```

---

## Quick Start

The most basic way to start a server:

```python
from reyserver import Server

server = Server(**server_args)

if __name__ == "__main__":

    server.run(**run_args)
```

Where:

* `Server`: The top-level server object provided by reyserver
* `server_args`: Server initialization parameters
* `run_args`: Server startup parameters

The `Server` object also provides convenient methods for adding other modules. You can compose authentication, database, file, cache, and other features according to your project requirements.

---

# Modules

reyserver is divided into multiple functional modules. Each module provides different backend service capabilities.

## `rserver` — Server Methods

**Top-level server module.**

Provides the top-level server object of reyserver and serves as the primary entry point for using the framework.

Main features:

* Create and configure the server object
* Add APIs provided by other modules
* Organize server functionality in a unified manner
* Start the server

Basic usage:

```python
from reyserver import Server

server = Server(**server_args)

if __name__ == "__main__":

    server.run(**run_args)
```

---

## `rall` — All Import Methods

**Unified export module.**

Provides convenient exports for all reyserver modules, methods, and objects. It allows framework functionality to be imported from a centralized module, reducing the need to import components separately from multiple modules.

---

## `rauth` — Authentication Methods

**User authentication module.**

Based on the **RBAC (Role-Based Access Control)** model, this module manages access permissions through users, roles, and permissions.

Main features:

* Supports `HTTPBearer`
* Supports `OAuth2PasswordBearer`
* User session state management
* User authentication APIs
* Create, update, and delete user information
* Automatically stores user information in the database
* Email verification
* SMS verification

---

## `rbase` — Base Methods

**Base utility module.**

Provides common methods and shared functionality used by other modules.

Main features:

* API exception methods

  * Specify HTTP response status codes
  * Automatically attach corresponding status code messages
* Pagination methods

  * Provides unified pagination handling
  * Standardizes pagination data structures
* Other common utility and dependency methods

---

## `rbind` — Dependency Bind Methods

**Dependency injection module.**

Provides convenient imports for commonly used dependency objects in route functions.

Through predefined singleton objects, API endpoints can easily access various contexts and resources during server operation.

For example:

* Global server object
* Current request object
* Database engine object
* Current authenticated user information
* Uploaded file data
* Parameter validation objects

Parameter validation objects include:

* IP address format validation
* Time format validation
* Other commonly used parameter validation utilities

The database engine supports ORM and provides automatic management of database session contexts.

---

## `rdb` — Database Methods

**Database module.**

Provides convenient methods for creating database APIs.

By specifying database table names, corresponding data APIs can be created quickly, reducing the amount of repetitive database API code that needs to be written.

---

## `rcache` — Cache Methods

**Cache module.**

Provides API caching capabilities based on **Redis**.

Main features:

* Route function caching decorators
* Cache expiration control
* Full-response caching for individual APIs
* Cache data separately based on API input parameters
* Redis-based cache storage

---

## `rfile` — File Methods

**File service module.**

Provides file upload, download, and file management APIs, including streaming downloads.

Architecture:

> File data is stored on disk, while file metadata is stored in the database.

Main features:

* File upload
* File download
* Streaming file download
* File metadata management through the database
* File visibility control
* Temporary signed URLs for downloads

Files support different visibility levels:

| Visibility | Description                                           |
| ---------- | ----------------------------------------------------- |
| Public     | Allows direct external access                         |
| Internal   | Only accessible internally or in authorized scenarios |
| Private    | Only accessible by the user who owns the file         |

Temporary signed URLs are also provided, allowing external users to access non-public files for a limited period without directly exposing the files to public access.

---

## `rlink` — Link Methods

**Short link module.**

Provides APIs for mapping long URLs to short URLs.

```text
Long URL → Short URL
```

It can be used for short URL generation, URL mapping, and similar scenarios.

---

## `rmiddleware` — Middleware Methods

**Middleware module.**

Provides middleware for route and response processing.

Main features:

* Automatic GZIP response compression
* GZIP compression path filtering
* Other route middleware functionality

---

## `rpublic` — Public Methods

**Public resource module.**

Provides APIs for website homepages, public files, and frontend static resources.

Main features:

* Homepage HTML file endpoint
* `public` file endpoint
* Frontend static file endpoint
* Frontend static route mapping

It is suitable for serving frontend build artifacts directly through the backend server.

---

## `rredirect` — Redirect Methods

**Request forwarding module.**

Provides server-wide request proxying and forwarding functionality.

Requests received by the current server can be forwarded to another server:

```text
Client

  │
  ▼
reyserver

  │
  ▼
Target Server
```

Suitable for API proxying, request forwarding, and similar scenarios.

---

## `rclient` — Client Methods

**Client module.**

Provides convenient client methods for calling APIs provided by the server.

Primarily used to encapsulate server API calls, such as:

* File processing APIs
* Testing APIs
* Other server APIs

---

## `rtest` — Test Methods

**Testing module.**

Provides server health and network performance testing APIs.

Main features:

* Server health checks
* API availability testing
* File upload speed testing
* File download speed testing
* Other server testing APIs

It can be used to verify server availability after deployment and measure network transmission performance.

---

# Module Overview

| Module          | Function                                                 |
| --------------- | -------------------------------------------------------- |
| `rserver`     | Top-level server object and server startup               |
| `rall`        | Unified exports for all methods                          |
| `rauth`       | User authentication, permissions, and session management |
| `rbase`       | Base methods and common utilities                        |
| `rbind`       | Route dependency injection                               |
| `rdb`         | Database APIs                                            |
| `rcache`      | Redis-based API caching                                  |
| `rfile`       | File upload, download, and management                    |
| `rlink`       | Long URL to short URL conversion                         |
| `rmiddleware` | Route and response middleware                            |
| `rpublic`     | Homepage, public files, and frontend static resources    |
| `rredirect`   | Request proxying and forwarding                          |
| `rclient`     | API client calls                                         |
| `rtest`       | Server testing and upload/download speed testing         |

---

# Dependencies

Main dependencies:

* `fastapi[standard]`
* `fastapi-cache2[redis]`
* `reyclient`
* `reydb`
* `reykit`
* `uvicorn[standard]`

---

# Project Information

| Project    | Information                                                |
| ---------- | ---------------------------------------------------------- |
| Name       | `reyserver`                                              |
| Version    | `1.1.288`                                                |
| Python     | `>=3.12`                                                 |
| Author     | `Rey`                                                      |
| Email      | `reyxbo@163.com`                                         |
| Homepage   | [reyxbo.com](https://www.reyxbo.com/release/python/reyserver) |
| Repository | [reyserver-py](https://github.com/reyxbo/reyserver-py.git)  |

## Keywords

`rey` · `reyxbo` · `server` · `backend` · `fastapi` · `API` · `async` · `asynchronous` · `cache` · `redis` · `file` · `link` · `public` · `redirect` · `RESTful`
