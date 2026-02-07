# Scheduler 服务需求设计文档

## 服务概述

Scheduler 是平台的计划任务服务，负责定时任务的管理，包括定时任务的添加、修改、删除、执行等。该服务提供 Web 界面和 API 接口，方便用户管理定时任务。

## 核心定位

- **任务调度**：统一管理所有定时任务
- **任务执行**：可靠执行定时任务
- **任务监控**：监控任务执行状态
- **任务管理**：提供任务管理界面和 API

## 技术栈

- **Web 框架**：基于 Base 服务（FastAPI）
- **部署方式**：Docker 镜像（基于 base 镜像）
- **调度引擎**：支持多种调度引擎（APScheduler、Celery Beat 等）
- **任务执行**：支持多种任务类型（Shell、Python、HTTP 等）

## 核心功能需求

### 1. 任务管理

#### 1.1 任务创建
- **任务基本信息**：
  - 任务名称（唯一标识）
  - 任务描述
  - 任务分组/分类
  - 任务标签
- **任务类型**：
  - Shell 命令任务
  - Python 脚本任务
  - HTTP 请求任务
  - 自定义脚本任务
- **任务配置**：
  - 任务参数
  - 环境变量
  - 工作目录
  - 超时设置

#### 1.2 任务编辑
- **基本信息修改**：修改任务名称、描述等
- **调度时间修改**：修改任务的调度时间
- **任务内容修改**：修改任务的执行内容
- **任务配置修改**：修改任务的配置参数

#### 1.3 任务删除
- **单个删除**：删除单个任务
- **批量删除**：批量删除多个任务
- **删除确认**：删除前确认提示
- **删除恢复**：支持任务删除恢复（可选）

#### 1.4 任务状态管理
- **启用/禁用**：启用或禁用任务
- **立即执行**：手动触发任务立即执行
- **停止执行**：停止正在执行的任务
- **任务克隆**：克隆现有任务创建新任务

### 2. 调度时间配置

#### 2.1 调度类型
- **间隔执行**：
  - 每隔 N 分钟执行
  - 每隔 N 小时执行
  - 每隔 N 天执行
- **每日执行**：
  - 每天指定时间执行
  - 支持多个时间点
- **每周执行**：
  - 每周指定日期和时间执行
  - 支持选择多个星期几
- **每月执行**：
  - 每月指定日期和时间执行
  - 支持月末执行
- **Cron 表达式**：
  - 支持标准 Cron 表达式
  - Cron 表达式验证和提示

#### 2.2 可视化时间选择器
- **时间选择界面**：
  - 图形化时间选择
  - 无需手动输入 Cron
  - 实时预览 Cron 表达式
- **时间预览**：
  - 显示下次执行时间
  - 显示未来 N 次执行时间
- **时间验证**：
  - 验证时间配置有效性
  - 提示配置错误

#### 2.3 高级调度选项
- **时区设置**：支持设置任务时区
- **开始时间**：设置任务开始生效时间
- **结束时间**：设置任务结束时间
- **执行次数限制**：限制任务执行次数

### 3. 任务执行

#### 3.1 执行引擎
- **本地执行**：在服务本地执行任务
- **远程执行**：通过 SSH 在远程服务器执行
- **容器执行**：在 Docker 容器中执行（可选）
- **分布式执行**：支持分布式任务执行（可选）

#### 3.2 任务类型支持

**Shell 命令任务**
- 执行 Shell 命令或脚本
- 支持环境变量
- 支持工作目录设置
- 支持超时控制

**Python 脚本任务**
- 执行 Python 代码
- 支持代码编辑器（带行号）
- 支持导入模块
- 支持代码验证

**HTTP 请求任务**
- 发送 HTTP 请求
- 支持 GET、POST、PUT、DELETE 等方法
- 支持请求头、请求体配置
- 支持认证配置

**自定义脚本任务**
- 支持其他脚本语言（可选）
- 支持自定义执行器

#### 3.3 执行控制
- **并发控制**：
  - 限制同时执行的任务数
  - 任务队列管理
- **重试机制**：
  - 任务失败自动重试
  - 重试次数和间隔配置
- **超时控制**：
  - 任务执行超时自动终止
  - 超时时间可配置
- **依赖管理**：
  - 任务执行依赖
  - 依赖任务完成后执行

### 4. 任务监控

#### 4.1 执行状态
- **状态类型**：
  - 等待中（Pending）
  - 执行中（Running）
  - 成功（Success）
  - 失败（Failed）
  - 已取消（Cancelled）
- **状态查询**：实时查询任务执行状态
- **状态通知**：任务状态变更通知

#### 4.2 执行历史
- **历史记录**：
  - 记录每次任务执行
  - 包括执行时间、耗时、状态等
- **历史查询**：
  - 按任务查询历史
  - 按时间范围查询
  - 按状态筛选
- **历史保留**：配置历史记录保留时间

#### 4.3 执行日志
- **日志记录**：
  - 记录任务执行日志
  - 标准输出和错误输出
- **日志查看**：
  - 实时查看执行日志
  - 查看历史日志
  - 日志搜索和过滤
- **日志导出**：导出日志文件

#### 4.4 执行统计
- **统计指标**：
  - 任务执行次数
  - 成功/失败次数
  - 平均执行时间
  - 成功率
- **统计报表**：
  - 按任务统计
  - 按时间统计
  - 可视化图表展示

### 5. 通知告警

#### 5.1 通知方式
- **邮件通知**：
  - 任务执行失败通知
  - 任务执行成功通知（可选）
- **Webhook 通知**：
  - 发送 HTTP 请求到指定 URL
  - 支持自定义请求格式
- **短信通知**（可选）：
  - 重要任务失败短信通知
- **站内通知**：
  - 平台内消息通知

#### 5.2 通知规则
- **触发条件**：
  - 任务执行失败
  - 任务执行超时
  - 任务连续失败 N 次
- **通知对象**：
  - 任务创建者
  - 指定通知人员
  - 通知组
- **通知频率**：
  - 每次失败都通知
  - 限制通知频率（避免骚扰）

### 6. 任务模板

#### 6.1 模板库
- **内置模板**：
  - 常用任务模板
  - 分类模板（备份、清理、监控等）
- **自定义模板**：
  - 用户创建自定义模板
  - 模板分享（可选）
- **模板使用**：
  - 使用模板快速创建任务
  - 模板参数化配置

#### 6.2 模板管理
- **模板创建**：创建新模板
- **模板编辑**：编辑现有模板
- **模板删除**：删除模板
- **模板导入导出**：模板的导入和导出

### 7. 任务分组

#### 7.1 分组管理
- **创建分组**：创建任务分组
- **分组编辑**：编辑分组信息
- **分组删除**：删除分组
- **分组权限**：分组级别的权限控制（可选）

#### 7.2 分组操作
- **批量操作**：
  - 批量启用/禁用
  - 批量删除
  - 批量导出
- **分组统计**：分组级别的执行统计

### 8. 权限管理

#### 8.1 任务权限
- **查看权限**：查看任务列表和详情
- **编辑权限**：创建和编辑任务
- **执行权限**：手动触发任务执行
- **删除权限**：删除任务
- **管理权限**：任务管理相关操作

#### 8.2 权限控制
- **用户权限**：基于用户的权限控制
- **角色权限**：基于角色的权限控制
- **任务级别权限**：任务级别的权限控制（可选）

## API 接口设计

### 任务管理 API

#### 获取任务列表
```
GET /api/scheduler/tasks?group=backup&status=active&page=1&limit=20

Response:
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "tasks": [
    {
      "id": "task-001",
      "name": "Daily Backup",
      "group": "backup",
      "status": "active",
      "schedule": "0 2 * * *",
      "next_run": "2024-01-02T02:00:00Z",
      "last_run": "2024-01-01T02:00:00Z",
      "last_status": "success"
    }
  ]
}
```

#### 创建任务
```
POST /api/scheduler/tasks
Content-Type: application/json

{
  "name": "Daily Backup",
  "description": "Daily database backup",
  "group": "backup",
  "type": "shell",
  "command": "/usr/bin/backup.sh",
  "schedule": {
    "type": "daily",
    "time": "02:00"
  },
  "enabled": true
}

Response:
{
  "id": "task-001",
  "name": "Daily Backup",
  "schedule": "0 2 * * *",
  "next_run": "2024-01-02T02:00:00Z"
}
```

#### 更新任务
```
PUT /api/scheduler/tasks/{task_id}
Content-Type: application/json

{
  "command": "/usr/bin/backup.sh",
  "schedule": {
    "type": "daily",
    "time": "03:00"
  }
}
```

#### 删除任务
```
DELETE /api/scheduler/tasks/{task_id}
```

#### 启用/禁用任务
```
POST /api/scheduler/tasks/{task_id}/enable
POST /api/scheduler/tasks/{task_id}/disable
```

#### 立即执行任务
```
POST /api/scheduler/tasks/{task_id}/run

Response:
{
  "execution_id": "exec-001",
  "status": "running"
}
```

### 执行历史 API

#### 获取执行历史
```
GET /api/scheduler/tasks/{task_id}/executions?page=1&limit=20

Response:
{
  "total": 100,
  "executions": [
    {
      "id": "exec-001",
      "task_id": "task-001",
      "status": "success",
      "started_at": "2024-01-01T02:00:00Z",
      "finished_at": "2024-01-01T02:05:00Z",
      "duration": 300,
      "output": "..."
    }
  ]
}
```

#### 获取执行详情
```
GET /api/scheduler/executions/{execution_id}

Response:
{
  "id": "exec-001",
  "task_id": "task-001",
  "status": "success",
  "started_at": "2024-01-01T02:00:00Z",
  "finished_at": "2024-01-01T02:05:00Z",
  "duration": 300,
  "output": "...",
  "error": null,
  "exit_code": 0
}
```

#### 获取执行日志
```
GET /api/scheduler/executions/{execution_id}/logs

Response:
{
  "logs": [
    {
      "timestamp": "2024-01-01T02:00:00Z",
      "level": "INFO",
      "message": "Task started"
    }
  ]
}
```

### 统计 API

#### 获取任务统计
```
GET /api/scheduler/tasks/{task_id}/stats?start_date=2024-01-01&end_date=2024-01-31

Response:
{
  "total_executions": 31,
  "success": 30,
  "failed": 1,
  "success_rate": 96.77,
  "avg_duration": 300,
  "total_duration": 9300
}
```

#### 获取全局统计
```
GET /api/scheduler/stats

Response:
{
  "total_tasks": 100,
  "active_tasks": 80,
  "total_executions": 1000,
  "success_rate": 95.5,
  "by_status": {
    "success": 955,
    "failed": 45
  }
}
```

### 模板 API

#### 获取模板列表
```
GET /api/scheduler/templates

Response:
{
  "templates": [
    {
      "id": "template-001",
      "name": "Database Backup",
      "category": "backup",
      "description": "..."
    }
  ]
}
```

#### 使用模板创建任务
```
POST /api/scheduler/tasks/from-template
Content-Type: application/json

{
  "template_id": "template-001",
  "name": "My Backup Task",
  "params": {
    "database": "mydb",
    "backup_path": "/backup"
  }
}
```

## 目录结构

```
scheduler/
├── etc/
│   └── config.yaml              # Scheduler 配置文件
├── module/
│   ├── scheduler_engine.py      # 调度引擎封装
│   ├── task_executor.py          # 任务执行器
│   ├── task_manager.py           # 任务管理器
│   └── notification.py           # 通知模块
├── service/
│   ├── scheduler_service.py      # 调度服务
│   ├── execution_service.py      # 执行服务
│   └── stats_service.py          # 统计服务
└── web/
    ├── manager/                  # 管理界面
    │   ├── index.html
    │   ├── tasks.html            # 任务管理页面
    │   ├── editor.html           # 任务编辑器页面
    │   ├── history.html          # 执行历史页面
    │   └── stats.html            # 统计页面
    └── api/                      # API 文档
```

## 配置示例

### config.yaml
```yaml
scheduler:
  # 调度引擎配置
  engine:
    type: apscheduler  # apscheduler, celery
    timezone: Asia/Shanghai
    max_workers: 10
  
  # 任务执行配置
  execution:
    timeout: 3600  # 默认超时时间（秒）
    retry:
      enabled: true
      max_attempts: 3
      delay: 60  # 重试延迟（秒）
    concurrency:
      max_concurrent: 5
  
  # 执行历史配置
  history:
    retention_days: 30
    max_records: 10000
  
  # 通知配置
  notification:
    email:
      enabled: true
      smtp_host: smtp.example.com
      smtp_port: 587
      smtp_user: scheduler@example.com
      smtp_password: ${SMTP_PASSWORD}
    webhook:
      enabled: true
      default_url: https://...
  
  # 存储配置
  storage:
    type: database  # database, redis
    database:
      url: sqlite:///scheduler.db
```

## 非功能性需求

### 性能要求
- **调度精度**：任务调度时间误差 < 1 秒
- **并发执行**：支持多任务并发执行
- **响应速度**：API 响应时间 < 500ms

### 可靠性要求
- **任务持久化**：任务配置持久化存储
- **故障恢复**：服务重启后恢复任务调度
- **执行可靠性**：任务执行失败自动重试
- **高可用**：服务可用性 > 99.9%

### 可扩展性要求
- **水平扩展**：支持多实例部署（需要分布式锁）
- **任务扩展**：支持自定义任务类型
- **执行器扩展**：支持自定义执行器

### 安全性要求
- **权限控制**：严格的权限控制
- **命令安全**：Shell 命令执行安全验证
- **数据加密**：敏感配置加密存储
- **操作审计**：完整的操作审计日志

## 依赖关系

### 依赖服务
- **Base 服务**：基于 base 镜像构建
- **Gateway 服务**：通过 Gateway 对外提供服务

### 外部依赖
- **调度库**：APScheduler、Celery Beat 等
- **执行环境**：Shell、Python 等

### 被依赖关系
- 其他服务可通过 Scheduler 管理定时任务

## 开发规范

### 代码规范
- 遵循 Base 服务的代码规范
- 使用类型提示
- 完整的文档字符串

### 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- 调度精度测试

### 文档要求
- API 文档完整
- 使用文档详细
- 示例任务丰富
