# Base 服务需求与实现进度

## 服务概述

Base 是平台的基础服务框架，提供整个项目中每个微服务的基础能力。该服务将作为基础镜像，其他微服务在制作镜像时以 base 镜像作为基础，并在其上进行开发。

## 核心定位

- **基础框架服务**：提供基本的 Web 服务、后台服务等核心功能
- **基础镜像**：作为 Docker 基础镜像，供其他微服务继承使用
- **通用能力提供**：提供配置管理、插件系统、模块系统、用户与 OAuth2 认证等通用能力

## 技术栈

- **Web 框架**：FastAPI
- **部署方式**：Docker 镜像
- **配置管理**：YAML 配置文件（config.yaml）+ 环境变量（.env）
- **会话/认证**：JWT（python-jose）、OAuth2 对接、系统级 Token
- **用户存储**：本地 users.json（由用户服务专控，jsonserv 排除）

---

## 当前目录结构（按实际代码）

```
base/
├── .env                        # 环境变量（可选）
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 镜像构建
├── etc/                        # 配置与数据
│   ├── config.yaml             # 主配置（支持热加载）
│   ├── sessions/               # Session 存储目录
│   └── data/                   # 数据目录（jsonserv 扫描 .json，users 由 user 服务专控）
├── logs/                       # 日志目录
├── main.py                     # 主程序入口
├── start.py                    # 启动命令
├── requirements.txt            # Python 依赖
├── core/                       # 核心路由与监控（当前实现）
│   ├── __init__.py
│   ├── file_watcher.py         # 目录监控：module/plugin/service/etc，变更回调
│   └── routes.py               # 路由注册：/health, /, /raw, /tree, /api/*, /openapi.json, /{path}
├── module/                     # 全局组件（变更自动加载/重载）
│   ├── __init__.py
│   ├── config.py               # 配置加载、环境变量替换、config.yaml 热加载
│   ├── logger.py               # 日志配置（级别、格式、轮转文件）
│   ├── markdown.py             # Markdown 渲染
│   └── webhandle.py            # Web 请求处理：动态加载 web/*.py，handle_request，sub_path
├── plugin/                     # 插件（变更自动加载/重载）
│   ├── __init__.py
│   └── router.py               # PluginManager、Plugin 基类、pre_process/post_process
├── service/                    # 后台服务
│   ├── __init__.py
│   ├── cron/                   # 计划任务（骨架，待实现）
│   │   └── __init__.py
│   ├── datasource/             # 多数据源（骨架，SQLite 待实现）
│   │   └── __init__.py
│   ├── jsonserv/               # JSON Mock 服务（已实现）
│   │   ├── __init__.py
│   │   ├── core.py             # JSONDataStore、CRUD、FileLock、查询过滤
│   │   └── router.py           # 扫描 etc/data/*.json，排除列表，注册 /api/jsonserv/*
│   └── user/                   # 用户管理服务（已实现）
│       ├── __init__.py
│       └── core.py             # UserService、本地/OAuth2 用户、密码 SHA256+bcrypt
└── web/                        # Web 与 API 根目录
    ├── __init__.py
    ├── index.html / index.md   # 站点首页
    ├── user.py                 # 用户 API：/api/user/*（登录、CRUD、改密）
    ├── example/
    │   └── hello.py            # 示例 API
    ├── login/
    │   ├── index.html
    │   └── oauth2.py           # OAuth2 登录入口与回调
    ├── extLogin/
    │   └── oauth2.py           # OAuth2 扩展登录（ExtLogin / extLogin）
    ├── config/
    │   └── oauth2.py          # OAuth2 相关配置接口
    ├── manager/                # 管理端（需管理员权限）
    │   ├── index.html
    │   ├── config.py           # /api/manager/config/*（如保存 OAuth2 配置）
    │   ├── oauth2/
    │   │   └── index.html
    │   └── user/
    │       └── index.html
    ├── app/
    │   └── index.html         # 应用入口
    ├── help/                   # 帮助与调试
    │   ├── index.html
    │   └── 01.md
    └── uploads/                # 上传目录
```

---

## 需求与实现状态总览

| 模块 | 需求摘要 | 实现状态 |
|------|----------|----------|
| 配置管理 | 主配置、环境变量、热加载、管理界面 | ✅ 已实现 config.yaml + 热加载 + manager 配置 API（如 OAuth2） |
| 模块系统 | module 自动加载、webhandle、markdown | ✅ 已实现，含 config、logger |
| 插件系统 | plugin 预处理/后处理、优先级 | ✅ 已实现 PluginManager、Plugin 基类 |
| 文件与目录 API | /raw、/tree 增删改查 | ✅ 已实现；tree 权限为 TODO |
| API 执行 | /api/{path} → web/{path}.py | ✅ 已实现，支持 sub_path 到 handle |
| API 认证 | Token（Header/参数）、系统 Token | ✅ 已实现；登录 Token 校验为 TODO |
| OpenAPI | 自动生成 /openapi.json | ⚠️ 当前为 app.openapi()，未按 web/*.py 聚合 |
| JSON Mock | jsonserv 扫描、CRUD、持久化、排除列表 | ✅ 已实现，users 排除由 user 服务专控 |
| 用户服务 | 本地用户、OAuth2 用户、密码哈希、users.json | ✅ 已实现（service/user + web/user.py） |
| OAuth2 | 对接第三方、登录/回调、管理端配置 | ✅ 已实现（login/oauth2、extLogin/oauth2、config、manager） |
| 多数据源 | datasource 配置与调用 | ⚠️ 骨架已实现，SQLite 待实现 |
| 计划任务 | cron 调度与执行 | ⚠️ 骨架已实现，逻辑待实现 |
| 自动加载 | 监控 module/plugin/service/etc | ✅ 已实现（core/file_watcher） |

---

## 1. 配置管理

### 1.1 配置文件结构（已实现）

- **主配置**：`etc/config.yaml`
- **环境变量**：支持 `.env`，配置项中可用 `${VAR}` 占位
- **热加载**：监控 `config.yaml` 变更，自动 `reload` 并应用（module/config.py + watchdog）
- **优先级**：环境变量 > config.yaml > 默认值

### 1.2 当前 config.yaml 主要项（已实现）

- `app`：name、version、debug
- `server`：host、port、reload
- `security`：secret_key、algorithm、access_token_expire_minutes、api_auth_enabled、system_tokens
- `logging`：level、format、file、max_bytes、backup_count
- `session`：storage_type、storage_path、expire_minutes
- `default_files`：首页默认文件列表（如 index.html、index.md、index.py）
- `oauth2`：enabled、server（host、protocol、authorize_path、token_path、resource_path、userinfo_path）、client、login、admin
- `upload`：max_size、allowed_extensions
- `jsonserv`：enabled、data_path、auto_reload、exclude_resources（如 users）

### 1.3 配置管理界面（部分已实现）

- 管理端入口：`web/manager/`（含 OAuth2、用户等子页）
- 配置保存 API：`web/manager/config.py`（如保存 OAuth2 配置到 config.yaml）
- 配置变更后通过热加载生效

---

## 2. 模块系统（已实现）

- **位置**：`module/`
- **加载**：file_watcher 监控，变更后触发重载
- **已用模块**：config、logger、markdown、webhandle
- **webhandle**：为 `web/` 下 Python 提供路由加载、`handle_request`、sub_path 分发

---

## 3. 插件系统（已实现）

- **位置**：`plugin/`
- **行为**：路由前 pre_process、路由后 post_process
- **实现**：PluginManager 扫描 plugin 目录、加载 Plugin 子类、按 priority 排序

---

## 4. 后台服务

### 4.1 jsonserv（已实现）

- 扫描 `etc/data/` 下所有 `.json`（含子目录），按文件名/相对路径生成资源名
- 支持根为数组或对象（含 primary_key）
- 排除列表：`jsonserv.exclude_resources`（如 `users`，由用户服务专控）
- 路由：`GET/POST /api/jsonserv/{resource}`、`GET/PUT/PATCH/DELETE /api/jsonserv/{resource}/{id}`
- 持久化：FileLock、实时写回、缩进格式化

### 4.2 user 服务（已实现）

- **数据**：`etc/data/users.json`，不由 jsonserv 暴露
- **能力**：本地用户（用户名+密码）、OAuth2 用户信息落库、角色 admin/user
- **密码**：SHA256 预处理 + bcrypt，兼容旧数据
- **API**：`web/user.py` 对接 `service/user/core.py`（登录、列表、创建、获取、更新、删除、改密）

### 4.3 datasource（骨架）

- 扫描 `service/datasource/` 下子目录，每目录 `config.yaml`
- 已定义 DataSource / FileDataSource / SQLiteDataSource、DataSourceManager
- SQLite 及具体 query/execute 待实现

### 4.4 cron（骨架）

- CronManager 在 main 启动/关闭时 start/stop
- 具体调度与执行逻辑待实现

---

## 5. API 与路由（已实现）

### 5.1 已注册路由

- `GET /health`：健康检查
- `GET /`：根路径，按 default_files 返回首页（html/md/py）
- `GET /raw/{path:path}`：读文件原始内容（支持 web/、etc/）；`PUT /raw/{path:path}`：写文件（写 config.yaml 后触发 config.reload）
- `GET/POST/PUT/DELETE /tree/{path:path}`：目录列表、创建、重命名、删除（权限 TODO）
- `GET/POST/PUT/DELETE /api/{path:path}`：转发到 webhandle，解析为 `web/{path}.py` + sub_path，调用 handle/main/handler
- `GET /openapi.json`：当前为 `app.openapi()`（未按 web/*.py 聚合）
- `GET /{path:path}`：目录则按 default_files 找默认文件；文件则按 .py/.md/.html 执行或返回

### 5.2 API 认证（已实现部分）

- `security.api_auth_enabled` 为 true 时，/api/* 需认证
- Token 来源：Header `Authorization: Bearer <token>` 或查询参数 `token=`
- 校验：与 `security.system_tokens` 比对；登录态 Token 校验为 TODO

### 5.3 用户与登录相关 API（已实现）

- `POST /api/user/login`：本地用户名密码登录，返回 JWT
- `GET /api/user` 或 `.../list`：用户列表
- `POST /api/user`：创建用户
- `GET/PUT|PATCH/DELETE /api/user/{id}`：单用户查改删
- `PUT|POST /api/user/{id}/password`：修改密码
- OAuth2：登录入口与回调在 `web/login/oauth2.py`、`web/extLogin/oauth2.py`

---

## 6. 前端与页面（已实现）

- 根路径及子路径按 `default_files` 解析目录默认页
- 每个子应用可有 `index.html` 等；管理端在 `web/manager/`（含 oauth2、user 等）
- 帮助与调试页面在 `web/help/`（如 01.md、index.html）

---

## 7. 自动加载机制（已实现）

- **core/file_watcher**：监控 module、plugin、service、etc
- 文件变更触发对应回调（如模块/插件/服务重载、配置重载）
- 与 main 启动时组件的初始化配合使用

---

## 8. 环境变量示例（.env）

```env
# 应用
APP_NAME=FastAPI Base Platform
APP_VERSION=1.0.0

# 安全（config 中可用 ${SECRET_KEY}）
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 日志
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log

# 服务
SERVER_HOST=0.0.0.0
SERVER_PORT=5000

# 会话
SESSION_SECRET=your_session_secret_here
```

---

## 9. 依赖（requirements.txt 当前）

- fastapi、uvicorn[standard]、python-dotenv、pyyaml、pydantic、pydantic-settings、python-multipart
- aiofiles、watchdog、filelock
- python-jose[cryptography]、passlib[bcrypt]、bcrypt
- markdown、pygments、jinja2、aiohttp

---

## 10. 待办与后续（按当前进度）

1. **计划任务**：在 cron 骨架基础上实现调度与执行（Shell/Python）、历史与日志
2. **数据源**：实现 SQLite（及可选其他）数据源的 query/execute
3. **OpenAPI**：按 web/*.py 自动汇总并生成 /openapi.json
4. **API 认证**：将登录 JWT 纳入 /api/* 校验（或对接 Session 服务）
5. **tree 接口**：为 /tree/* 增加权限校验
6. **App 管理**：若需“上传/卸载 App 包、管理界面”，在现有 web/manager 与服务骨架基础上扩展
7. **配置管理**：如需更完整的配置项增删改查与界面，在现有 manager/config 上扩展

---

## 11. 非功能性需求（参考）

- 性能：API 响应、并发、异步文件操作
- 可靠性：优雅关闭、健康检查（已提供 /health）
- 安全：敏感配置走环境变量、HTTPS、输入校验与 XSS 防护
- 可维护性：日志、调试模式、监控指标
