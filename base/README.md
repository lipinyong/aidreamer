# Base Platform

基于 FastAPI 的基础服务平台，作为其他微服务的基础镜像。

## 功能特性

- ✅ 配置管理（YAML + 环境变量，支持热加载）
- ✅ 模块系统（全局可调用组件）
- ✅ 插件系统（路由前后处理）
- ✅ 后台服务（jsonserv、数据源、计划任务）
- ✅ API 接口（/raw, /tree, /api, /）
- ✅ Markdown 渲染
- ✅ 文件监控和自动加载
- ✅ Token 认证
- ✅ Web 前端页面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 为 `.env` 并修改配置（如果需要）。

### 3. 启动服务

```bash
python start.py
```

或使用 Docker：

```bash
docker-compose up
```

### 4. 访问服务

- 首页: http://localhost:5000/
- 配置管理: http://localhost:5000/manager
- API 文档: http://localhost:5000/help
- 健康检查: http://localhost:5000/health

## 项目结构

```
base/
├── etc/              # 配置文件目录
│   ├── config.yaml   # 主配置文件
│   ├── data/         # jsonserv 数据文件
│   └── sessions/     # Session 存储
├── module/           # 全局模块
│   ├── config.py     # 配置管理
│   ├── logger.py     # 日志管理
│   ├── webhandle.py  # Web 处理
│   └── markdown.py   # Markdown 渲染
├── plugin/           # 插件目录
├── service/          # 后台服务
│   ├── jsonserv/     # JSON Mock 服务
│   ├── datasource/   # 数据源服务
│   └── cron/         # 计划任务
├── web/              # Web 前端
│   ├── app/          # 应用页面
│   ├── manager/      # 配置管理页面
│   ├── help/         # 帮助文档
│   └── example/      # 示例代码
├── core/             # 核心功能
│   ├── file_watcher.py  # 文件监控
│   └── routes.py     # 路由设置
├── main.py           # 主程序入口
└── start.py          # 启动脚本
```

## 开发指南

### 创建 API 接口

在 `web/` 目录下创建 Python 文件：

```python
from module.webhandle import webhandle
from fastapi import Request

@webhandle.route('/example/hello')
def hello(request: Request):
    return {'message': 'Hello, World!'}
```

访问: `GET /api/example/hello`

### 使用数据源

```python
from service.datasource import get_datasource

ds = get_datasource('db')
result = ds.query('SELECT * FROM users')
```

### 创建插件

在 `plugin/` 目录下创建插件文件：

```python
from plugin.router import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("my_plugin", priority=100)
    
    async def pre_process(self, request):
        # 预处理逻辑
        return request
    
    async def post_process(self, request, response):
        # 后处理逻辑
        return response
```

### jsonserv 使用

在 `etc/data/` 目录下创建 JSON 文件：

```json
{
  "primary_key": "id",
  "data": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

自动生成 API:
- `GET /api/jsonserv/users` - 获取列表
- `GET /api/jsonserv/users/1` - 获取单条
- `POST /api/jsonserv/users` - 新增
- `PUT /api/jsonserv/users/1` - 更新
- `DELETE /api/jsonserv/users/1` - 删除

## API 接口

### 基础接口

- `GET /raw/{path}` - 读取文件原始内容
- `GET /tree/{path}` - 列出目录
- `POST /tree/{path}` - 创建文件/目录
- `PUT /tree/{path}` - 重命名
- `DELETE /tree/{path}` - 删除
- `GET /api/{path}` - 执行 Python 文件（需要 Token）
- `GET /{path}` - Web 访问（自动处理 .py, .md, .html）

### 认证

访问 `/api/*` 接口需要 Token：

1. Header: `Authorization: Bearer <token>`
2. 查询参数: `?token=<token>`

Token 来源：
- 系统级 Token（在 config.yaml 中配置）
- 登录 Token（待实现）

## 配置说明

主要配置在 `etc/config.yaml`：

```yaml
app:
  name: FastAPI Base Platform
  version: 1.0.0

server:
  host: 0.0.0.0
  port: 5000

security:
  system_tokens:
    - token: your-token-here
      description: 系统 Token

jsonserv:
  enabled: true
  data_path: etc/data
```

## Docker 部署

### 构建镜像

```bash
docker build -t baseplatform:latest .
```

### 运行容器

```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/etc:/app/etc \
  -v $(pwd)/web:/app/web \
  baseplatform:latest
```

## 开发计划

- [ ] Session 管理集成
- [ ] OAuth2 完整实现
- [ ] 计划任务完整实现
- [ ] SQLite 数据源实现
- [ ] App 管理系统
- [ ] 权限管理系统
- [ ] 更多插件示例

## 许可证

MIT License
