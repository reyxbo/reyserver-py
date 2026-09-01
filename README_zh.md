
# reyserver

**reyserver** 是一个基于 [FastAPI](https://fastapi.tiangolo.com/) 的后端异步服务器集成 API 框架包。

提供认证、数据库、缓存、文件、短链接、请求转发、中间件、静态资源等常用后端服务能力，并通过统一的服务器对象和依赖注入机制，简化后端 API 服务的开发。

整体遵循 **RESTful** 风格，适用于构建异步 Web API 和后端服务。

## 特性

* 基于 FastAPI 的异步 API 框架
* 遵循 RESTful API 设计风格
* 模块化设计，可按需组合服务器功能
* 提供统一的服务器对象和启动方式
* 支持 RBAC 用户认证与权限管理
* 支持 `HTTPBearer` 和 `OAuth2PasswordBearer`
* 提供用户会话状态管理
* 支持数据库及 ORM
* 提供基于 Redis 的接口缓存
* 提供文件上传、下载和流式下载
* 支持文件公开、内部和用户私有等可见性控制
* 提供临时文件下载签名 URL
* 提供长 URL 转短 URL
* 提供服务器请求代理转发
* 提供 GZIP 响应压缩及过滤中间件
* 提供前端静态资源和公共文件服务
* 提供服务存活检查及上传下载测速接口
* 提供常用依赖注入对象和参数验证工具

---

## 安装

要求 **Python 3.12 或更高版本**。

```bash
pip install reyserver
```

---

## 快速开始

最基本的服务器启动方式：

```python
from reyserver import Server

server = Server(**server_args)

if __name__ == "__main__":
    server.run(**run_args)
```

其中：

* `Server`：reyserver 提供的顶层服务器对象
* `server_args`：服务器初始化参数
* `run_args`：服务器启动参数

`Server` 对象同时提供添加其它模块接口的便捷方法，可以根据项目需求组合认证、数据库、文件、缓存等功能。

---

# 模块

reyserver 按功能划分为多个模块，各模块负责不同的后端服务能力。

## `rserver` — Server methods

**顶层服务器模块。**

提供 reyserver 的顶层服务器对象，是使用框架的主要入口。

主要功能：

* 创建和配置服务器对象
* 添加其它模块提供的 API
* 统一组织服务器功能
* 启动服务器

基本使用方式：

```python
from reyserver import Server

server = Server(**server_args)

if __name__ == "__main__":
    server.run(**run_args)
```

---

## `rall` — All import methods

**统一导出模块。**

提供 reyserver 所有模块方法和对象的便捷导出，可以通过该模块集中导入框架提供的功能，减少从多个模块分别导入的代码。

---

## `rauth` — Authentication methods

**用户认证模块。**

基于 **RBAC（Role-Based Access Control，基于角色的访问控制）** 模型，从用户、角色和权限三个维度管理访问权限。

主要功能：

* 支持 `HTTPBearer`
* 支持 `OAuth2PasswordBearer`
* 用户会话信息状态管理
* 用户认证 API
* 用户信息增、删、改
* 用户信息自动写入数据库
* 邮箱验证
* 手机短信验证

---

## `rbase` — Base methods

**基础方法模块。**

提供其它模块共用的基础方法和公共功能。

主要包括：

* 接口跳出方法

  * 可指定 HTTP 响应状态码
  * 自动附加对应的状态码信息文本
* 分页方法

  * 提供统一的分页处理
  * 规范分页数据结构
* 其它基础工具和公共依赖方法

---

## `rbind` — Dependency bind methods

**依赖注入模块。**

提供路由函数中常用依赖对象的便捷导入。

通过预定义的单例对象，可以在 API 接口中方便地获取服务器运行过程中的各种上下文对象和资源。

例如：

* 全局服务器对象
* 当前请求对象
* 数据库引擎对象
* 当前会话用户信息
* 上传文件数据
* 参数验证对象

参数验证对象包括：

* IP 地址格式验证
* 时间格式验证
* 其它常用参数格式验证

数据库引擎支持 ORM，并提供数据库会话上下文的自动管理。

---

## `rdb` — Database methods

**数据库模块。**

提供数据库接口的便捷创建方法。

通过指定数据库表名，可以快速创建对应名称的数据接口，减少重复编写数据库 API 的工作量。

---

## `rcache` — Cache methods

**缓存模块。**

基于 **Redis** 提供 API 接口缓存能力。

主要功能：

* 路由函数缓存装饰器
* 缓存过期控制
* 单接口全量缓存
* 根据接口输入参数分别缓存对应数据
* Redis 缓存存储

---

## `rfile` — File methods

**文件服务模块。**

提供文件上传、下载及文件管理接口，并支持流式下载。

采用：

> 文件数据存储在磁盘，文件信息存储在数据库。

主要功能：

* 文件上传
* 文件下载
* 流式文件下载
* 文件信息数据库管理
* 文件可见性控制
* 临时下载签名 URL

文件支持不同的可见性：

| 可见性 | 说明                     |
| ------ | ------------------------ |
| 公开   | 允许外部直接访问         |
| 内部   | 仅允许内部或授权场景访问 |
| 私有   | 仅允许文件所属用户访问   |

同时提供临时下载签名 URL，使外部用户可以在有限时间内访问非公开文件，而无需直接开放文件访问权限。

---

## `rlink` — Link methods

**短链接模块。**

提供长 URL 到短 URL 的映射接口。

```text
长 URL → 短 URL
```

可用于短链接生成和 URL 映射等场景。

---

## `rmiddleware` — Middleware methods

**中间件模块。**

提供路由及响应处理相关的中间件。

主要包括：

* 响应数据自动 GZIP 压缩
* GZIP 压缩路径过滤
* 其它路由中间件功能

---

## `rpublic` — Public methods

**公共资源模块。**

提供网站主页、公共文件和前端静态资源相关接口。

主要包括：

* 主页 HTML 文件接口
* `public` 公共文件接口
* 前端静态文件接口
* 前端静态路由映射接口

适用于将前端构建产物直接集成到后端服务器中。

---

## `rredirect` — Redirect methods

**请求转发模块。**

提供服务器全局请求代理转发功能。

可以将当前服务器收到的请求转发到其它服务器：

```text
客户端
  │
  ▼
reyserver
  │
  ▼
目标服务器
```

适用于 API 代理、请求转发等场景。

---

## `rclient` — Client methods

**客户端模块。**

提供用于调用本服务器 API 的便捷客户端方法。

主要用于封装服务器接口调用，例如：

* 文件处理接口
* 测试接口
* 其它服务器 API

---

## `rtest` — Test methods

**测试模块。**

提供服务器运行状态和网络性能测试接口。

主要包括：

* 服务存活检查
* 接口可用性测试
* 文件上传测速
* 文件下载测速
* 其它服务器测试接口

可用于服务器部署后的运行状态检查以及网络传输性能测试。

---

# 模块概览

| 模块            | 功能                         |
| --------------- | ---------------------------- |
| `rserver`     | 顶层服务器对象及服务器启动   |
| `rall`        | 所有方法的统一导出           |
| `rauth`       | 用户认证、权限及会话管理     |
| `rbase`       | 基础方法及公共功能           |
| `rbind`       | 路由依赖注入                 |
| `rdb`         | 数据库接口                   |
| `rcache`      | Redis 接口缓存               |
| `rfile`       | 文件上传、下载及文件管理     |
| `rlink`       | 长 URL 转短 URL              |
| `rmiddleware` | 路由及响应中间件             |
| `rpublic`     | 主页、公共文件及前端静态资源 |
| `rredirect`   | 请求代理转发                 |
| `rclient`     | API 客户端调用               |
| `rtest`       | 服务测试及上传下载测速       |

---

# 依赖

主要依赖：

* `fastapi[standard]`
* `fastapi-cache2[redis]`
* `reyclient`
* `reydb`
* `reykit`
* `uvicorn[standard]`

---

# 项目信息

| 项目       | 信息                                                       |
| ---------- | ---------------------------------------------------------- |
| 名称       | `reyserver`                                              |
| 版本       | `1.1.288`                                                |
| Python     | `>=3.12`                                                 |
| 作者       | Rey                                                        |
| 邮箱       | `reyxbo@163.com`                                         |
| Homepage   | [reyxbo.com](https://reyxbo.com:2/release/python/reyserver) |
| Repository | [reyserver-py](https://github.com/reyxbo/reyserver-py.git)  |

## 关键词

`rey` · `reyxbo` · `server` · `backend` · `fastapi` · `API` · `async` · `asynchronous` · `cache` · `redis` · `file` · `link` · `public` · `redirect` · `RESTful`
