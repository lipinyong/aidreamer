使用fastapi编写一个web服务，名字叫baseplatform，使用中文回复
## 基本要求
1. 这是一个基本框架，使用fastapi搭建的web服务
2. 将以这个框架为基础，做成基础镜像，其他的微服务可以基于这个镜像进行构建
3. 包含的主要目录应该有：
- etc：存放配置文件，默认配置文件是config.yaml
- module: 整个需要都需要使用的全局模块
- plugin：插件目录，存放插件，在路由前进行预处理，在路由后进行后处理
- service：后台服务
- sessions：存放session信息
- web：前端页面
- web/help：帮助文档
4. etc、service、plugin目录能够实现监控，自动加载生效
5. 可使用页面进行配置
6. 可进行类app的管理(上传部署和卸载)，app包里应该包括配置，后台服务，全局模块、前端页面、api接口和说明文档，安装部署时将包里的内容分别放到对应的目录下
7. 有简单的权限管理，支持对接第三方的oauth2服务

说明：
- 这里所说的app不是主流意义上的app，仅仅是在此平台下的，通过安装部署不同的app，平台实现不同的功能应用
- 后端存在插件、模块和后台服务：
    - 插件在路由前进行预处理，在路由后进行后处理
    - 后台服务是程序启动时加载的，在程序运行期间一直存在，能够动态加载，但是唯一的
    - 模块是可以全局调用的组件，调用模块时生成的对象不是唯一的

## 项目目录结构
```
.
├── .env                        # 环境变量文件
├── docker-compose.yml          # Docker 编排文件
├── Dockerfile                  # Docker 镜像构建文件
├── etc/                        # 配置文件目录
│   ├── config.yaml             # 主配置文件
│   ├── sessions/               # Session 存储目录
│   └── data/                   # 数据目录
├── logs                        # 日志目录
├── main.py                     # 主程序入口
├── module/                     # 全局组件目录(添加/变动后自动加载/重载)
│   ├── __init__.py
│   ├── markdown.py             # Markdown 渲染器
│   └── webhandle.py            # Web服务处理模块handle(request)
├── plugin/                     # 插件目录(添加/变动后自动加载/重载)
│   ├── __init__.py
│   └── router.py               # 动态路由管理
├── requirements.txt            # Python 依赖
├── service/                    # 后台服务目录
│   ├── __init__.py
│   ├── cron/                   # 计划任务
│   ├── datasource/             # 数据源服务目录
│   └── jsonserv/               # 针对json的mock服务，参考json-server
│       ├── __init__.py
│       ├── core.py             # 核心逻辑：JSON读写、查询过滤算法
│       └── router.py           # 动态路由注册入口
├── start.py                    # 启动命令
└── web/                        # Web 服务根目录
    ├── __init__.py
    ├── app/                    # app前端目录
    │   ├── __init__.py
    │   ├── index.html          # 应用首页
    ├── help/                   # 帮助文件
    ├── index.md                # 首页（Markdown）
    ├── login/                  # 登录相关
    ├── manager/                # 页面化配置管理系统(管理员权限)
    │   └── index.html          # 配置管理页面
    └── uploads                # 文件上传目录
```
### .env文件配置
```
# Application Settings
APP_NAME=FastAPI Base Platform
APP_VERSION=1.0.0

# Security Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging Settings
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# Server Settings
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
# 会话密钥 (用于 JWT 签名)
SESSION_SECRET=your_session_secret_here
```

## API 需求
### 基本的API 接口

1. `/raw/{path}` - 文件读写，py文件不执行，md文件不渲染，直接输出原内容，不支持两进制文件
2. `/tree/{path}` - 目录管理，在有权限的情况下(默认)，可列子目录和文件，可创建、删除、重命名文件和目录
3. `/api/{path}` - API 执行，查找path是否是py文件，有则加载运行，没有则返回404的json数据格式。示例访问/api/example/hello，则检查web/example/hello.py文件是否存在，存在则运行并返回结果
4. `/{path}` - 浏览器访问，如果path是目录，则查找该目录下是否有默认文件，有则自动定位到该文件。默认文件的配置在config.yml中，是一个数组，按照优先级从第一个单元开始。如果是path是否是py文件，有则运行并返回结果，如果path是否是md文件，是则进行html渲染后再返回前端，没有则404
监控config.yml，当出现变更后自动重新加载并应用配置，比如修改了端口，服务自动重启，设计方案允许加载和卸载的方式新增新的服务和页面

注意：
- 所有的在web目录下的py文件，都需要在module.webhandle.handle(request)中进行处理
- 所有的在web目录下的py文件，可以使用接口`/{path}`进行访问，其中path是文件的路径，需要扩展名，相对于web目录
- 所有的在web目录西的py文件，可以使用接口/api/{path}` - API 执行，查找path是否是py文件
- 所有的在web目录下的md文件，在第一次运行时可以自主加载到/openapi.json,后续运行时如果py文件有变更，会自动重载并更新到/openapi.json
- 前端的/docs取消，在web/help目录下设计调试页面。
- 所有在web目录下的html页面都需要包含以下脚本：
```javascript
const BASE_PATH = (function() {
    const path = window.location.pathname;
    const idx = path.indexOf('/<pagefile>');
    return idx > 0 ? path.substring(0, idx) : '';
})();
```

### API Token 认证
- **Token 来源**：
    1. 登录成功后自动生成的临时 Token。
    2. 在 `config.yaml` 中静态配置的“系统级 Token”（用于脚本调用或预授权访问）。
- **验证**：访问 `/api/*` 时，必须在 Header (如 `Authorization: Bearer <token>`) 或参数中携带 Token。

## jsonserv 服务
`jsonserv` 模块旨在提供一个零编码的 Mock API 服务。系统应能自动扫描指定目录下的 `.json` 数据文件，并根据文件内容自动生成符合 RESTful 规范的 CRUD 接口。该服务主要用于前端开发调试或快速原型搭建。

### 数据源管理
*   **自动发现**: 服务启动时，需自动扫描 `etc/data/` 目录下包括子目录下的所有 `.json` 文件。
*   **路由映射规则**:
    *   以文件名作为一级路由前缀。
    *   **场景 A (列表模式)**: 如果 `todos.json` 的根是一个数组 `[...]`，则映射路由为 `/api/todos`和`/api/jsonserv/todos`。
    *   **场景 B (对象模式)**: 如果 `db.json` 的根是一个对象 `{"posts": [], "comments": []}`，则映射路由为 `/api/db/posts` 和 `/api/db/comments`或 `/api/jsonserv/db/posts` 和 `/api/jsonserv/db/comments`(参考 json-server 的标准行为)。
    *   *建议默认采用场景 A，即一个文件对应一个资源集合，方便管理。*

### 接口规范 (CRUD)
对于每个被扫描到的资源（例如 `etc/data/jsonserv/products.json`），自动挂载以下 FastAPI 路由：

*   **GET** `/api/jsonserv/products`: 获取列表（支持分页、筛选、排序）。
*   **GET** `/api/jsonserv/products/{id}`: 根据 ID 获取单条数据。
*   **POST** `/api/jsonserv/products`: 新增数据。
    *   系统应自动生成唯一 `id` (若请求体未包含)。
    *   数据需持久化写入对应的 JSON 文件。
*   **PUT** `/api/jsonserv/products/{id}`: 全量更新指定 ID 的数据。
*   **PATCH** `/api/jsonserv/products/{id}`: 局部更新指定 ID 的数据。
*   **DELETE** `/api/jsonserv/products/{id}`: 删除指定 ID 的数据。

### 高级查询支持 (Query Parameters)
模仿 `json-server` 的查询参数风格，实现以下功能：

*   **分页**: 支持 `_page` 和 `_limit` 参数。
    *   例: `GET /api/jsonserv/products?_page=1&_limit=10`
*   **排序**: 支持 `_sort` (字段名) 和 `_order` (asc/desc)。
    *   例: `GET /api/jsonserv/products?_sort=price&_order=desc`
*   **切片**: 支持 `_start` 和 `_end` 或 `_limit`。
*   **全文搜索**: 支持 `q` 参数（可选需求）。
*   **字段过滤**: 直接使用字段名作为参数。
    *   例: `GET /api/jsonserv/products?category=electronics&published=true`

### 数据持久化与并发控制
*   **实时写入**: 所有写操作 (POST/PUT/PATCH/DELETE) 必须实时更新对应的 `.json` 物理文件，确保重启服务后数据不丢失。
*   **并发安全**: 由于文件操作涉及 IO，需使用文件锁（如 `filelock` 库）或单线程写入队列，防止多请求并发写入时导致 JSON 文件损坏。
*   **格式化**: 写入文件时应保持 JSON 的缩进（Indent=2或4），保证文件可读性。

### 技术实现建议 (Technical Notes)

*   **路由构建**: 使用 `fastapi.APIRouter` 动态构建路由。由于 Pydantic 模型需要预定义，对于动态 JSON 结构，Request Body 和 Response Model 应使用 `Dict[str, Any]` 或 `List[Dict[str, Any]]`。
*   **ID 处理**: 默认支持 `id` 字段为整型或 UUID 字符串。
*   **异常处理**:
    *   文件格式错误（非标准 JSON）应在启动时报错或跳过并在日志中记录。
    *   找不到 ID 返回 404。

### 示例数据结构
假设文件 `etc/data/users.json` ：

```json
[
  { "id": 1, "name": "Alice", "role": "developer" },
  { "id": 2, "name": "Bob", "role": "designer" }
]
```

访问效果：
*   `GET /api/jsonserv/users/1` -> 返回 Alice 的数据。
*   `GET /api/jsonserv/users?role=developer` -> 返回包含 Alice 的列表。

#### 扩展应用
假设json数据如下:
```json
{
    "primary_key":"username",
    "data":[
        {"username":"20110032","name":"张三","age":20,"role":["admin","user"],"email":"zhangsan@example.com"},
        {"username":"20110033","name":"李四","age":21,"role":["user"],"email":"lisi@example.com"}
    ]
}
```
则访问效果:
*   `GET /api/jsonserv/users/data/20110032` -> 返回张三的数据。
*   `GET /api/jsonserv/users/data?role=admin` -> 返回包含张三的列表。
*   `GET /api/jsonserv/users/data` -> 返回数据列表。
*   `GET /api/jsonserv/users/data?_page=1&_limit=10` -> 分页查询，返回第 1 页的数据。
*   `POST /api/jsonserv/users/data` -> 新增用户数据，并返回新增后的完整列表。
*   `PUT /api/users/data/20110033` -> 更新李四的数据，并返回更新后的完整列表。

### 高级应用
还是之前的json数据，如果需要读取/更新张三的名字，需要使用primary_key作为路径参数，如下：
*   `GET /api/jsonserv/users/data/20110032/cname` -> 返回张三的名字。
*   `PUT /api/jsonserv/users/data/20110032/cname` -> 更新张三的名字，并返回更新后的完整列表。

默认主键是id，也可以通过`primary_key`指定其他字段作为主键。


## module/webhandle的说明
module目录下的文件都是其他模块通过import调用的，在web目录下的py文件可以通过/api/的方式实现调用，比如web/example/hello.py，则可以访问/api/example/hello
所以在hello.py中定义一个函数，然后在webhandle.py中导入并注册到路由上，形式如下：
```python
from module.webhandle import WebHandle

@webhandle.route('/example/hello')
def hello(requst):
    return 'hello world'
```


## 多数据源
多数据源实际是一种后台服务，在service/datasource目录下，每个子目录都是一个数据源，每个子目录下都有一个config.yaml文件，用于配置该数据源的连接信息，比如数据库连接信息、文件路径等。

其他代码可以调用service/datasource目录下的数据源服务，比如在web/example/hello.py中调用数据源服务，如下：
```python
from module.webhandle import WebHandle
from module.datasource import DataSource

@webhandle.route('/example/hello')
def hello(requst):
    ds = DataSource('db')
    return ds.query('select * from users')
```

## 计划任务管理

管理后台定时任务，支持可视化配置调度时间。

**功能特性：**

- 创建、编辑、删除计划任务
- 可视化调度时间选择器（无需手动输入 Cron）
- 执行 Shell 命令或 Python 代码
- 带行号的代码编辑器
- 任务启动/停止控制
- 立即执行任务
- 查看执行历史和日志

**调度类型：**

| 类型 | 说明 |
| ---- | ---- |
| 间隔执行 | 每隔指定分钟/小时执行 |
| 每日执行 | 每天指定时间执行 |
| 每周执行 | 每周指定日期和时间执行 |
| 每月执行 | 每月指定日期和时间执行 |

## 前端页面
- 前端页面在web目录下，每个子目录都是一个应用，每个应用下都有一个index.html文件，作为该应用的入口文件
- 前端页面可以通过BASE_PATH来访问，比如BASE_PATH是/api，那么访问/api/example/hello.html就会调用web/example/hello.py文件。
- 每个网页实际是一个页面容器，对应有一个js文件，js文件的文件名就是网页的文件名，比如hello.html对应的js文件就是hello.js。
- 每个js文件中都需要包含一个init函数，用于初始化页面，比如hello.js中需要包含以下代码：
```javascript
function init(dom) {
    // 初始化页面
}
```
- 支持在其他页面里调用该js，可以在一个桌面的html容器里，形成页面内的子窗口，并调用指定的js，渲染子窗口的内容。


## 其他需求
使用中文回复