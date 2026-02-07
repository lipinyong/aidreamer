# Linux Panel 服务需求设计文档

## 服务概述

Linux Panel 是平台的 Linux 面板服务，负责 Linux 服务器和关键进程的管理，包括监控、日志、文件管理、系统管理等。该服务提供 Web 界面和 API 接口，方便用户管理 Linux 服务器。

## 核心定位

- **服务器管理**：统一管理 Linux 服务器
- **进程管理**：管理关键进程的启动、停止、监控
- **系统监控**：监控系统资源使用情况
- **日志管理**：集中管理和查看系统日志
- **文件管理**：提供文件系统的 Web 管理界面

## 技术栈

- **Web 框架**：基于 Base 服务（FastAPI）
- **部署方式**：Docker 镜像（基于 base 镜像）
- **系统调用**：通过 SSH 或本地执行系统命令
- **监控技术**：系统指标采集和展示

## 核心功能需求

### 1. 服务器管理

#### 1.1 服务器连接管理
- **连接方式**：
  - SSH 连接（推荐）
  - 本地连接（同一主机）
  - Agent 连接（安装 Agent 程序）
- **连接配置**：
  - 服务器名称、地址、端口
  - 认证方式（密码、密钥）
  - 连接超时设置
- **连接测试**：测试服务器连接是否正常
- **连接状态**：实时显示服务器连接状态

#### 1.2 服务器分组
- **分组管理**：支持服务器分组管理
- **分组标签**：支持为服务器添加标签
- **批量操作**：支持对分组内的服务器进行批量操作

#### 1.3 服务器信息
- **系统信息**：
  - 操作系统版本
  - 内核版本
  - 主机名
  - 运行时间
- **硬件信息**：
  - CPU 信息
  - 内存信息
  - 磁盘信息
  - 网络信息

### 2. 系统监控

#### 2.1 实时监控
- **CPU 监控**：
  - CPU 使用率（总体、每个核心）
  - CPU 负载（1分钟、5分钟、15分钟）
  - CPU 温度（如果支持）
- **内存监控**：
  - 内存使用率
  - 内存总量、已用、可用
  - Swap 使用情况
- **磁盘监控**：
  - 磁盘使用率
  - 磁盘 I/O（读写速度、IOPS）
  - 磁盘空间（总量、已用、可用）
- **网络监控**：
  - 网络流量（入站、出站）
  - 网络连接数
  - 网络接口状态

#### 2.2 历史数据
- **数据存储**：存储历史监控数据
- **数据查询**：支持查询指定时间范围的监控数据
- **数据展示**：以图表形式展示历史数据
- **数据导出**：支持导出监控数据（CSV、JSON）

#### 2.3 监控告警
- **告警规则**：
  - CPU 使用率超过阈值
  - 内存使用率超过阈值
  - 磁盘使用率超过阈值
  - 进程异常退出
- **告警通知**：
  - 邮件通知
  - 短信通知（可选）
  - Webhook 通知
- **告警历史**：记录告警历史

### 3. 进程管理

#### 3.1 进程监控
- **进程列表**：显示所有运行中的进程
- **进程信息**：
  - 进程 ID（PID）
  - 进程名称
  - CPU 使用率
  - 内存使用量
  - 运行时间
  - 启动命令
- **进程搜索**：支持按名称、用户等搜索进程
- **进程排序**：支持按 CPU、内存等排序

#### 3.2 进程控制
- **启动进程**：
  - 支持启动指定命令
  - 支持后台运行
  - 支持设置工作目录、环境变量
- **停止进程**：
  - 支持优雅停止（SIGTERM）
  - 支持强制停止（SIGKILL）
- **重启进程**：支持重启进程
- **进程守护**：支持将进程设置为守护进程（自动重启）

#### 3.3 进程组管理
- **进程组定义**：将相关进程组织成进程组
- **批量操作**：支持对进程组进行批量启动、停止、重启
- **依赖管理**：支持设置进程启动依赖

### 4. 日志管理

#### 4.1 日志查看
- **系统日志**：
  - `/var/log/syslog`
  - `/var/log/messages`
  - `/var/log/kern.log`
- **应用日志**：
  - 自定义日志文件路径
  - 支持多个日志文件
- **实时日志**：支持实时查看日志（类似 `tail -f`）
- **日志搜索**：支持关键词搜索日志
- **日志过滤**：支持按时间、级别等过滤日志

#### 4.2 日志级别
- **级别定义**：DEBUG、INFO、WARNING、ERROR、CRITICAL
- **级别过滤**：支持按日志级别过滤
- **级别统计**：统计各级别日志数量

#### 4.3 日志管理
- **日志轮转**：支持日志轮转配置
- **日志清理**：支持自动清理过期日志
- **日志归档**：支持日志归档和压缩
- **日志导出**：支持导出日志文件

### 5. 文件管理

#### 5.1 文件浏览
- **目录浏览**：支持浏览服务器文件系统
- **文件列表**：
  - 文件名、大小、修改时间
  - 文件权限、所有者
  - 文件类型
- **路径导航**：支持路径导航和快速跳转
- **文件搜索**：支持按名称搜索文件

#### 5.2 文件操作
- **文件上传**：
  - 支持单文件上传
  - 支持多文件上传
  - 支持拖拽上传
  - 支持上传进度显示
- **文件下载**：
  - 支持文件下载
  - 支持目录打包下载
- **文件编辑**：
  - 支持在线编辑文本文件
  - 支持代码高亮
  - 支持保存和撤销
- **文件删除**：
  - 支持删除文件和目录
  - 支持批量删除
  - 删除前确认
- **文件重命名**：支持重命名文件和目录
- **文件移动/复制**：支持移动和复制文件

#### 5.3 权限管理
- **权限查看**：查看文件和目录权限
- **权限修改**：支持修改文件和目录权限（chmod）
- **所有者修改**：支持修改文件所有者（chown）

### 6. 系统管理

#### 6.1 系统服务管理
- **服务列表**：显示系统服务列表（systemd）
- **服务状态**：显示服务运行状态
- **服务控制**：
  - 启动服务
  - 停止服务
  - 重启服务
  - 重载服务配置
- **服务自启**：设置服务开机自启

#### 6.2 软件包管理
- **包管理器支持**：
  - apt（Debian/Ubuntu）
  - yum/dnf（CentOS/RHEL）
  - pacman（Arch Linux）
- **软件包查询**：查询已安装的软件包
- **软件包安装**：安装软件包
- **软件包更新**：更新软件包
- **软件包卸载**：卸载软件包

#### 6.3 用户管理
- **用户列表**：显示系统用户列表
- **用户信息**：显示用户详细信息
- **用户创建**：创建新用户
- **用户删除**：删除用户
- **用户修改**：修改用户信息
- **权限管理**：管理用户权限（sudo）

#### 6.4 网络管理
- **网络接口**：显示网络接口信息
- **IP 配置**：查看和配置 IP 地址
- **路由表**：查看路由表
- **防火墙**：管理防火墙规则（iptables、firewalld）

### 7. 计划任务管理

#### 7.1 Cron 任务
- **任务列表**：显示所有 Cron 任务
- **任务创建**：创建新的 Cron 任务
- **任务编辑**：编辑现有 Cron 任务
- **任务删除**：删除 Cron 任务
- **任务执行**：立即执行 Cron 任务
- **执行历史**：查看任务执行历史

#### 7.2 任务模板
- **模板库**：提供常用任务模板
- **模板使用**：使用模板快速创建任务

### 8. 安全功能

#### 8.1 访问控制
- **权限管理**：控制用户对服务器的访问权限
- **操作审计**：记录所有操作日志
- **会话管理**：管理用户会话

#### 8.2 安全扫描
- **漏洞扫描**：扫描系统漏洞（可选）
- **安全建议**：提供安全加固建议

## API 接口设计

### 服务器管理 API

#### 获取服务器列表
```
GET /api/linux-panel/servers

Response:
{
  "servers": [
    {
      "id": "server-001",
      "name": "Web Server 1",
      "address": "192.168.1.100",
      "port": 22,
      "status": "connected",
      "os": "Ubuntu 22.04",
      "uptime": "10 days"
    }
  ]
}
```

#### 添加服务器
```
POST /api/linux-panel/servers
Content-Type: application/json

{
  "name": "Web Server 2",
  "address": "192.168.1.101",
  "port": 22,
  "auth_type": "key",
  "key_path": "/path/to/key"
}
```

### 监控 API

#### 获取实时监控数据
```
GET /api/linux-panel/servers/{server_id}/monitor

Response:
{
  "cpu": {
    "usage": 45.5,
    "load": [1.2, 1.5, 1.8],
    "cores": 4
  },
  "memory": {
    "total": 8192,
    "used": 4096,
    "available": 4096,
    "usage": 50.0
  },
  "disk": {
    "total": 100000,
    "used": 50000,
    "available": 50000,
    "usage": 50.0
  },
  "network": {
    "in": 1000,
    "out": 500
  }
}
```

#### 获取历史监控数据
```
GET /api/linux-panel/servers/{server_id}/monitor/history?start=2024-01-01&end=2024-01-31

Response:
{
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "cpu": 45.5,
      "memory": 50.0,
      "disk": 50.0
    }
  ]
}
```

### 进程管理 API

#### 获取进程列表
```
GET /api/linux-panel/servers/{server_id}/processes

Response:
{
  "processes": [
    {
      "pid": 1234,
      "name": "nginx",
      "cpu": 2.5,
      "memory": 1024,
      "user": "www-data",
      "command": "/usr/sbin/nginx"
    }
  ]
}
```

#### 启动进程
```
POST /api/linux-panel/servers/{server_id}/processes/start
Content-Type: application/json

{
  "command": "/usr/sbin/nginx",
  "args": ["-g", "daemon off;"],
  "working_dir": "/etc/nginx",
  "env": {"VAR": "value"}
}
```

#### 停止进程
```
POST /api/linux-panel/servers/{server_id}/processes/{pid}/stop
```

### 日志管理 API

#### 获取日志
```
GET /api/linux-panel/servers/{server_id}/logs?path=/var/log/syslog&lines=100

Response:
{
  "logs": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "level": "INFO",
      "message": "System started"
    }
  ]
}
```

#### 实时日志（SSE）
```
GET /api/linux-panel/servers/{server_id}/logs/stream?path=/var/log/syslog

Response (SSE):
data: {"timestamp": "...", "level": "INFO", "message": "..."}
```

### 文件管理 API

#### 列出目录
```
GET /api/linux-panel/servers/{server_id}/files?path=/home/user

Response:
{
  "path": "/home/user",
  "files": [
    {
      "name": "file.txt",
      "type": "file",
      "size": 1024,
      "modified": "2024-01-01T00:00:00Z",
      "permissions": "644"
    }
  ]
}
```

#### 上传文件
```
POST /api/linux-panel/servers/{server_id}/files/upload
Content-Type: multipart/form-data

{
  "path": "/home/user",
  "file": <file>
}
```

#### 下载文件
```
GET /api/linux-panel/servers/{server_id}/files/download?path=/home/user/file.txt
```

## 目录结构

```
linux-panel/
├── etc/
│   └── config.yaml              # Linux Panel 配置文件
├── module/
│   ├── ssh_client.py             # SSH 客户端模块
│   ├── system_monitor.py         # 系统监控模块
│   ├── process_manager.py        # 进程管理模块
│   ├── log_manager.py            # 日志管理模块
│   └── file_manager.py          # 文件管理模块
├── service/
│   ├── monitor_service.py        # 监控服务
│   ├── alert_service.py          # 告警服务
│   └── data_collector.py         # 数据采集服务
└── web/
    ├── manager/                  # 管理界面
    │   ├── index.html
    │   ├── servers.html          # 服务器管理页面
    │   ├── monitor.html          # 监控页面
    │   ├── processes.html        # 进程管理页面
    │   ├── logs.html             # 日志查看页面
    │   └── files.html            # 文件管理页面
    └── api/                      # API 文档
```

## 配置示例

### config.yaml
```yaml
linux_panel:
  # 默认连接配置
  default_ssh:
    port: 22
    timeout: 30
    key_path: /etc/ssh/keys
  
  # 监控配置
  monitor:
    interval: 60  # 采集间隔（秒）
    retention_days: 30  # 数据保留天数
    metrics:
      - cpu
      - memory
      - disk
      - network
  
  # 告警配置
  alerts:
    enabled: true
    rules:
      - metric: cpu.usage
        threshold: 80
        duration: 300
      - metric: memory.usage
        threshold: 90
        duration: 300
    notifications:
      - type: email
        recipients: [admin@example.com]
  
  # 日志配置
  logs:
    default_paths:
      - /var/log/syslog
      - /var/log/messages
    max_lines: 10000
    retention_days: 7
```

## 非功能性需求

### 性能要求
- **低延迟**：SSH 操作响应时间 < 5s
- **高并发**：支持同时管理多台服务器
- **数据采集**：监控数据采集不影响服务器性能

### 可靠性要求
- **连接重试**：SSH 连接失败时自动重试
- **错误处理**：完善的错误处理和提示
- **数据备份**：监控数据定期备份

### 安全性要求
- **认证安全**：安全的 SSH 密钥管理
- **权限控制**：严格的权限控制
- **操作审计**：完整的操作审计日志
- **数据加密**：敏感数据加密存储

### 可扩展性要求
- **多服务器**：支持管理大量服务器
- **插件扩展**：支持自定义监控指标
- **协议扩展**：支持新的连接协议

## 依赖关系

### 依赖服务
- **Base 服务**：基于 base 镜像构建
- **Gateway 服务**：通过 Gateway 对外提供服务

### 系统依赖
- **SSH 客户端**：用于连接远程服务器
- **系统命令**：执行系统管理命令

### 被依赖关系
- 其他服务可通过 Linux Panel 管理服务器

## 开发规范

### 代码规范
- 遵循 Base 服务的代码规范
- 使用类型提示
- 完整的文档字符串

### 测试要求
- 单元测试覆盖率 > 70%
- 集成测试覆盖主要功能
- Mock 测试覆盖 SSH 操作

### 文档要求
- API 文档完整
- 使用文档详细
- 安全文档清晰
