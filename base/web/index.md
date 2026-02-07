# Base Platform

欢迎使用 Base Platform！

这是一个基于 FastAPI 的基础服务平台，提供以下功能：

## 核心功能

- **配置管理**：支持 YAML 配置文件和环境变量
- **模块系统**：全局可调用的组件模块
- **插件系统**：支持路由前后处理插件
- **后台服务**：支持多种后台服务（jsonserv、数据源、计划任务等）
- **API 接口**：提供丰富的 API 接口
- **Web 前端**：支持 Markdown 和 HTML 页面

## 快速开始

1. 访问 `/manager` 进行配置管理
2. 访问 `/help` 查看帮助文档
3. 访问 `/api/openapi.json` 查看 API 文档

## 开发指南

在 `web/` 目录下创建 Python 文件即可自动注册为 API 接口。

示例：创建 `web/example/hello.py`：

```python
from module.webhandle import webhandle

@webhandle.route('/example/hello')
def hello(request):
    return {'message': 'Hello, World!'}
```

然后可以通过 `/api/example/hello` 访问。
