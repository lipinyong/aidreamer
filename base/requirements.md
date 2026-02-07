# Base 服务需求设计文档

## 服务概述

Base 是平台的基础服务框架，提供整个项目中每个微服务的基础能力。该服务将作为基础镜像，其他微服务在制作镜像时以 base 镜像作为基础，并在其上进行开发。

## 核心定位

- **基础框架服务**：提供基本的 Web 服务、后台服务等核心功能
- **基础镜像**：作为 Docker 基础镜像，供其他微服务继承使用
- **通用能力提供**：提供配置管理、插件系统、模块系统、权限管理等通用能力

## 技术栈

- **Web 框架**：FastAPI
- **部署方式**：Docker 镜像
- **配置管理**：YAML 配置文件（config.yaml）
- **会话管理**：支持 Session 存储
- **权限认证**：支持 OAuth2 对接

## 目录结构

```
base/
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
    └── uploads                 # 文件上传目录
```

## 核心功能需求

### 1. 配置管理

#### 1.1 配置文件结构
- **主配置文件**：`etc/config.yaml`
- **环境变量**：`.env` 文件支持
- **配置热加载**：监控 `config.yaml` 变更，自动重新加载并应用配置
- **配置优先级**：环境变量 > config.yaml > 默认值

#### 1.2 配置项要求
- 应用基本信息（名称、版本等）
- 安全配置（密钥、Token 过期时间等）
- 日志配置（级别、格式、文件路径等）
- 服务器配置（主机、端口等）
- 会话配置（存储方式、过期时间等）
- 默认文件配置（数组形式，按优先级排序）

#### 1.3 配置管理界面
- 提供页面化配置管理系统（`web/manager/`）
- 支持管理员权限控制
- 支持配置的增删改查
- 配置变更后自动生效

### 2. 模块系统

#### 2.1 模块定义
- **位置**：`module/` 目录
- **特性**：全局可调用的组件
- **加载方式**：自动监控目录变化，自动加载/重载
- **调用方式**：通过 `import` 导入使用
- **对象特性**：调用模块时生成的对象不是唯一的

#### 2.2 核心模块

**webhandle.py**
- 提供 Web 服务处理模块
- 支持路由注册装饰器
- 处理请求和响应
- 支持在 `web/` 目录下的 Python 文件通过装饰器注册路由

**markdown.py**
- 提供 Markdown 渲染功能
- 支持 Markdown 文件转换为 HTML
- 支持自定义渲染选项

### 3. 插件系统

#### 3.1 插件定义
- **位置**：`plugin/` 目录
- **特性**：在路由前进行预处理，在路由后进行后处理
- **加载方式**：自动监控目录变化，自动加载/重载
- **执行时机**：
  - 预处理：路由匹配前执行
  - 后处理：路由处理完成后执行

#### 3.2 插件接口
- 提供标准的插件接口规范
- 支持插件链式执行
- 支持插件优先级配置
- 支持插件启用/禁用

### 4. 后台服务系统

#### 4.1 服务定义
- **位置**：`service/` 目录
- **特性**：程序启动时加载，在程序运行期间一直存在
- **加载方式**：支持动态加载，但服务实例唯一
- **服务类型**：
  - 计划任务服务（`cron/`）
  - 数据源服务（`datasource/`）
  - JSON Mock 服务（`jsonserv/`）

#### 4.2 服务管理
- 支持服务的启动、停止、重启
- 支持服务状态监控
- 支持服务配置管理

### 5. API 接口系统

#### 5.1 基础 API 接口

**文件读写接口**
- `GET /raw/{path}` - 读取文件原始内容
  - 支持文本文件读取
  - Python 文件不执行，直接输出原内容
  - Markdown 文件不渲染，直接输出原内容
  - 不支持二进制文件

**目录管理接口**
- `GET /tree/{path}` - 列出目录和文件
- `POST /tree/{path}` - 创建文件或目录
- `DELETE /tree/{path}` - 删除文件或目录
- `PUT /tree/{path}` - 重命名文件或目录
- 支持权限控制（默认有权限）

**API 执行接口**
- `GET /api/{path}` - 执行 Python 文件
  - 查找 `web/{path}.py` 文件
  - 存在则加载运行并返回结果
  - 不存在则返回 404 JSON 格式
  - 示例：访问 `/api/example/hello`，检查 `web/example/hello.py` 是否存在

**Web 访问接口**
- `GET /{path}` - 浏览器访问
  - 如果 path 是目录，查找该目录下的默认文件（按 config.yaml 配置的优先级）
  - 如果 path 是 Python 文件，执行并返回结果
  - 如果 path 是 Markdown 文件，渲染为 HTML 后返回
  - 否则返回 404

#### 5.2 API Token 认证

**Token 来源**
1. 登录成功后自动生成的临时 Token
2. 在 `config.yaml` 中静态配置的"系统级 Token"（用于脚本调用或预授权访问）

**验证方式**
- 访问 `/api/*` 时，必须在 Header（`Authorization: Bearer <token>`）或参数中携带 Token
- 支持 Token 过期时间配置
- 支持 Token 刷新机制

#### 5.3 OpenAPI 文档
- 所有在 `web/` 目录下的 Python 文件，在第一次运行时自动加载到 `/openapi.json`
- 如果 Python 文件有变更，自动重载并更新 `/openapi.json`
- 取消 FastAPI 默认的 `/docs` 页面，在 `web/help/` 目录下设计调试页面

### 6. JSON Mock 服务（jsonserv）

#### 6.1 数据源管理
- **自动发现**：服务启动时，自动扫描 `etc/data/` 目录下包括子目录下的所有 `.json` 文件
- **路由映射规则**：
  - 以文件名作为一级路由前缀
  - **场景 A（列表模式）**：如果 JSON 文件的根是一个数组 `[...]`，则映射路由为 `/api/todos` 和 `/api/jsonserv/todos`
  - **场景 B（对象模式）**：如果 JSON 文件的根是一个对象 `{"posts": [], "comments": []}`，则映射路由为 `/api/db/posts` 和 `/api/db/comments` 或 `/api/jsonserv/db/posts` 和 `/api/jsonserv/db/comments`

#### 6.2 CRUD 接口规范
对于每个被扫描到的资源（例如 `etc/data/jsonserv/products.json`），自动挂载以下 FastAPI 路由：
- `GET /api/jsonserv/products` - 获取列表（支持分页、筛选、排序）
- `GET /api/jsonserv/products/{id}` - 根据 ID 获取单条数据
- `POST /api/jsonserv/products` - 新增数据（自动生成唯一 ID，持久化写入）
- `PUT /api/jsonserv/products/{id}` - 全量更新指定 ID 的数据
- `PATCH /api/jsonserv/products/{id}` - 局部更新指定 ID 的数据
- `DELETE /api/jsonserv/products/{id}` - 删除指定 ID 的数据

#### 6.3 高级查询支持
- **分页**：支持 `_page` 和 `_limit` 参数
- **排序**：支持 `_sort`（字段名）和 `_order`（asc/desc）
- **切片**：支持 `_start` 和 `_end` 或 `_limit`
- **全文搜索**：支持 `q` 参数（可选）
- **字段过滤**：直接使用字段名作为参数

#### 6.4 数据持久化
- **实时写入**：所有写操作必须实时更新对应的 `.json` 物理文件
- **并发安全**：使用文件锁或单线程写入队列，防止并发写入导致文件损坏
- **格式化**：写入文件时保持 JSON 缩进（Indent=2 或 4）

#### 6.5 扩展功能
- 支持自定义主键（通过 `primary_key` 字段指定，默认为 `id`）
- 支持嵌套字段访问（如 `/api/jsonserv/users/data/20110032/cname`）

### 7. 多数据源服务

#### 7.1 数据源配置
- **位置**：`service/datasource/` 目录
- **配置方式**：每个子目录都是一个数据源，每个子目录下都有一个 `config.yaml` 文件
- **配置内容**：数据源的连接信息（数据库连接信息、文件路径等）

#### 7.2 数据源调用
- 提供统一的 `DataSource` 接口
- 支持在代码中通过名称调用数据源
- 示例：`ds = DataSource('db')`，然后 `ds.query('select * from users')`

### 8. 计划任务管理

#### 8.1 功能特性
- 创建、编辑、删除计划任务
- 可视化调度时间选择器（无需手动输入 Cron）
- 执行 Shell 命令或 Python 代码
- 带行号的代码编辑器
- 任务启动/停止控制
- 立即执行任务
- 查看执行历史和日志

#### 8.2 调度类型
- **间隔执行**：每隔指定分钟/小时执行
- **每日执行**：每天指定时间执行
- **每周执行**：每周指定日期和时间执行
- **每月执行**：每月指定日期和时间执行

### 9. App 管理系统

#### 9.1 App 定义
- **说明**：这里的 App 不是主流意义上的 App，仅仅是在此平台下的功能应用
- **功能**：通过安装部署不同的 App，平台实现不同的功能应用

#### 9.2 App 包结构
App 包应该包括：
- 配置文件
- 后台服务
- 全局模块
- 前端页面
- API 接口
- 说明文档

#### 9.3 App 管理功能
- **上传部署**：上传 App 包，安装部署时将包里的内容分别放到对应的目录下
- **卸载**：卸载已安装的 App，清理相关文件
- **管理界面**：提供 App 管理界面，支持查看、启用、禁用、卸载等操作

### 10. 权限管理系统

#### 10.1 基本权限管理
- 提供简单的权限管理功能
- 支持用户角色管理
- 支持权限分配

#### 10.2 OAuth2 对接
- 支持对接第三方的 OAuth2 服务
- 支持多种 OAuth2 提供商
- 支持 Token 管理和刷新

### 11. 前端页面系统

#### 11.1 页面结构
- **位置**：`web/` 目录
- **组织方式**：每个子目录都是一个应用，每个应用下都有一个 `index.html` 文件作为入口文件

#### 11.2 页面访问
- 前端页面可以通过 `BASE_PATH` 来访问
- 每个网页实际是一个页面容器，对应有一个 JS 文件
- JS 文件的文件名就是网页的文件名（如 `hello.html` 对应 `hello.js`）

#### 11.3 页面初始化
- 每个 JS 文件中都需要包含一个 `init` 函数，用于初始化页面
- 支持在其他页面里调用该 JS，可以在一个桌面的 HTML 容器里，形成页面内的子窗口

#### 11.4 BASE_PATH 脚本
所有在 `web/` 目录下的 HTML 页面都需要包含以下脚本：
```javascript
const BASE_PATH = (function() {
    const path = window.location.pathname;
    const idx = path.indexOf('/<pagefile>');
    return idx > 0 ? path.substring(0, idx) : '';
})();
```

### 12. 自动加载机制

#### 12.1 监控目录
- `etc/` 目录：配置文件变更自动重新加载
- `module/` 目录：模块添加/变动后自动加载/重载
- `plugin/` 目录：插件添加/变动后自动加载/重载
- `service/` 目录：服务添加/变动后自动加载/重载

#### 12.2 加载策略
- 文件系统监控：使用文件系统事件监控目录变化
- 热重载：支持不重启服务的情况下重新加载变更
- 错误处理：加载失败时记录日志，不影响服务运行

## 环境变量配置

### .env 文件配置示例
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

## Docker 镜像要求

### 基础镜像
- 基于 Python 官方镜像（建议 Python 3.11+）
- 安装必要的系统依赖

### 镜像构建
- 提供 `Dockerfile` 用于构建基础镜像
- 提供 `docker-compose.yml` 用于本地开发测试
- 镜像应包含所有基础依赖和框架代码

### 镜像标签
- 使用版本标签管理不同版本的镜像
- 支持多架构构建（amd64、arm64）

## 非功能性需求

### 性能要求
- API 响应时间 < 200ms（P95）
- 支持并发请求处理
- 文件操作支持异步处理

### 可靠性要求
- 服务可用性 > 99.9%
- 支持优雅关闭
- 支持健康检查接口

### 安全性要求
- 所有敏感配置通过环境变量管理
- 支持 HTTPS
- 输入验证和 SQL 注入防护
- XSS 防护

### 可维护性要求
- 代码注释完整
- 日志记录详细
- 支持调试模式
- 提供监控指标接口

## 依赖关系

### 外部依赖
- FastAPI 框架
- Python 标准库
- 文件系统（用于配置、数据存储）

### 被依赖关系
- 所有其他微服务都基于 base 镜像构建
- Gateway 服务需要 base 提供的认证能力
- Sessions 服务需要 base 提供的会话管理能力

## 开发规范

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用类型提示（Type Hints）
- 函数和类需要文档字符串

### 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- 提供测试文档

### 文档要求
- API 文档自动生成
- 提供开发指南
- 提供部署文档
