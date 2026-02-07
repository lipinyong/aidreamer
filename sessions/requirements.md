# Sessions 服务需求设计文档

## 服务概述

Sessions 是平台的全局 Sessions 共享服务，负责统一管理所有微服务的会话信息。其他容器通过这个服务共享 Sessions，实现跨服务的会话一致性。

## 核心定位

- **会话存储中心**：统一存储所有微服务的会话数据
- **会话共享**：实现跨微服务的会话共享
- **会话管理**：提供会话的创建、查询、更新、删除等操作
- **会话同步**：确保多个服务实例间的会话数据一致性

## 技术栈

- **Web 框架**：基于 Base 服务（FastAPI）
- **部署方式**：Docker 镜像（基于 base 镜像）
- **存储后端**：支持多种存储后端（Redis、内存、文件系统等）
- **会话协议**：支持标准 Session 协议

## 核心功能需求

### 1. 会话存储

#### 1.1 存储后端支持
- **Redis 存储**（推荐）：
  - 高性能、高可用
  - 支持集群模式
  - 支持持久化
- **内存存储**：
  - 适用于单实例部署
  - 重启后数据丢失
- **文件系统存储**：
  - 适用于小规模部署
  - 数据持久化到磁盘
- **数据库存储**（可选）：
  - 支持关系型数据库（MySQL、PostgreSQL）
  - 支持 NoSQL 数据库（MongoDB）

#### 1.2 存储结构
- **会话 ID**：唯一标识符（支持 UUID、自定义格式）
- **会话数据**：键值对形式存储
- **元数据**：
  - 创建时间
  - 最后访问时间
  - 过期时间
  - 所属用户 ID（可选）
  - 客户端 IP（可选）
  - User-Agent（可选）

#### 1.3 数据序列化
- **序列化格式**：
  - JSON（默认，推荐）
  - Pickle（Python 专用）
  - MessagePack（高效二进制格式）
- **数据压缩**：支持大数据的压缩存储（可选）

### 2. 会话操作

#### 2.1 创建会话
- **接口**：`POST /api/sessions`
- **功能**：
  - 创建新的会话
  - 生成唯一的会话 ID
  - 设置初始会话数据
  - 设置过期时间
- **参数**：
  - `data`：初始会话数据（JSON 对象）
  - `expires_in`：过期时间（秒，可选）
  - `user_id`：用户 ID（可选）
- **返回**：会话 ID 和会话信息

#### 2.2 获取会话
- **接口**：`GET /api/sessions/{session_id}`
- **功能**：
  - 根据会话 ID 获取会话数据
  - 更新最后访问时间
  - 检查会话是否过期
- **返回**：会话数据或 404（不存在/已过期）

#### 2.3 更新会话
- **接口**：`PUT /api/sessions/{session_id}`
- **功能**：
  - 更新会话数据
  - 支持部分更新（PATCH）和全量更新（PUT）
  - 更新最后访问时间
- **参数**：
  - `data`：要更新的会话数据（JSON 对象）
  - `merge`：是否合并更新（默认 true）

#### 2.4 删除会话
- **接口**：`DELETE /api/sessions/{session_id}`
- **功能**：
  - 删除指定会话
  - 支持批量删除（可选）

#### 2.5 会话续期
- **接口**：`POST /api/sessions/{session_id}/refresh`
- **功能**：
  - 延长会话过期时间
  - 更新最后访问时间
- **参数**：
  - `expires_in`：新的过期时间（秒）

### 3. 会话查询

#### 3.1 按条件查询
- **接口**：`GET /api/sessions`
- **查询参数**：
  - `user_id`：按用户 ID 查询
  - `ip`：按客户端 IP 查询
  - `created_after`：创建时间之后
  - `created_before`：创建时间之前
  - `expired`：是否已过期（true/false）
- **返回**：会话列表（支持分页）

#### 3.2 会话统计
- **接口**：`GET /api/sessions/stats`
- **功能**：
  - 总会话数
  - 活跃会话数（最近 N 分钟有访问）
  - 过期会话数
  - 按用户统计会话数

### 4. 会话过期管理

#### 4.1 过期策略
- **TTL（Time To Live）**：
  - 每个会话设置过期时间
  - 支持固定过期时间和滑动过期时间
- **空闲过期**：
  - 基于最后访问时间的过期
  - 超过指定时间未访问自动过期
- **绝对过期**：
  - 基于创建时间的过期
  - 创建后固定时间过期

#### 4.2 过期清理
- **主动清理**：
  - 定期扫描过期会话并删除
  - 可配置清理间隔
- **被动清理**：
  - 访问时检查过期，过期则删除
- **批量清理**：
  - 支持批量删除过期会话
  - 支持按条件批量删除

### 5. 会话安全

#### 5.1 会话 ID 安全
- **ID 生成**：
  - 使用加密安全的随机数生成器
  - 支持自定义 ID 格式
  - ID 长度和复杂度可配置
- **ID 验证**：
  - 验证 ID 格式
  - 防止 ID 猜测攻击

#### 5.2 访问控制
- **IP 绑定**（可选）：
  - 会话与客户端 IP 绑定
  - IP 变更时要求重新认证
- **User-Agent 绑定**（可选）：
  - 会话与 User-Agent 绑定
  - 检测异常访问

#### 5.3 会话劫持防护
- **Token 验证**：
  - 支持额外的安全 Token
  - Token 与 Session ID 绑定
- **异常检测**：
  - 检测异常访问模式
  - 自动失效可疑会话

### 6. 会话同步

#### 6.1 多实例同步
- **问题**：多个 Sessions 服务实例间的数据一致性
- **解决方案**：
  - 使用共享存储（Redis、数据库）
  - 使用消息队列同步（可选）
  - 使用分布式锁保证一致性

#### 6.2 缓存策略
- **本地缓存**：
  - 在服务实例本地缓存热点会话
  - 减少对存储后端的访问
- **缓存失效**：
  - 支持缓存失效通知
  - 支持主动刷新缓存

### 7. 性能优化

#### 7.1 读写优化
- **批量操作**：
  - 支持批量读取会话
  - 支持批量写入会话
- **异步操作**：
  - 支持异步读写
  - 提高并发性能

#### 7.2 缓存优化
- **多级缓存**：
  - 本地内存缓存
  - 分布式缓存（Redis）
- **缓存预热**：
  - 启动时预热热点数据

### 8. 监控与日志

#### 8.1 会话监控
- **实时统计**：
  - 当前会话数
  - 创建速率
  - 访问速率
  - 过期速率
- **存储监控**：
  - 存储使用量
  - 存储性能指标

#### 8.2 日志记录
- **操作日志**：
  - 记录所有会话操作（创建、更新、删除）
  - 包括操作时间、操作类型、会话 ID 等
- **访问日志**：
  - 记录会话访问情况
  - 包括访问时间、客户端信息等
- **错误日志**：
  - 记录所有错误信息
  - 包括错误类型、错误消息等

#### 8.3 指标导出
- **Prometheus 集成**：支持 Prometheus 指标导出
- **指标类型**：
  - Counter：会话创建数、删除数等
  - Gauge：当前会话数、存储使用量等
  - Histogram：操作响应时间分布等

## API 接口设计

### 会话操作 API

#### 创建会话
```
POST /api/sessions
Content-Type: application/json

{
  "data": {
    "user_id": "user-001",
    "username": "admin",
    "role": "admin"
  },
  "expires_in": 3600,
  "user_id": "user-001"
}

Response:
{
  "session_id": "sess-abc123...",
  "expires_at": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T11:00:00Z"
}
```

#### 获取会话
```
GET /api/sessions/{session_id}

Response:
{
  "session_id": "sess-abc123...",
  "data": {
    "user_id": "user-001",
    "username": "admin",
    "role": "admin"
  },
  "created_at": "2024-01-01T11:00:00Z",
  "last_accessed_at": "2024-01-01T11:30:00Z",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

#### 更新会话
```
PUT /api/sessions/{session_id}
Content-Type: application/json

{
  "data": {
    "role": "super_admin"
  },
  "merge": true
}

PATCH /api/sessions/{session_id}
Content-Type: application/json

{
  "data": {
    "role": "super_admin"
  }
}
```

#### 删除会话
```
DELETE /api/sessions/{session_id}

Response: 204 No Content
```

#### 会话续期
```
POST /api/sessions/{session_id}/refresh
Content-Type: application/json

{
  "expires_in": 7200
}

Response:
{
  "session_id": "sess-abc123...",
  "expires_at": "2024-01-01T13:00:00Z"
}
```

### 会话查询 API

#### 查询会话列表
```
GET /api/sessions?user_id=user-001&page=1&limit=20

Response:
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "sessions": [
    {
      "session_id": "sess-abc123...",
      "user_id": "user-001",
      "created_at": "2024-01-01T11:00:00Z",
      "expires_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### 会话统计
```
GET /api/sessions/stats

Response:
{
  "total": 1000,
  "active": 800,
  "expired": 200,
  "by_user": {
    "user-001": 5,
    "user-002": 3
  }
}
```

### 批量操作 API

#### 批量获取会话
```
POST /api/sessions/batch
Content-Type: application/json

{
  "session_ids": ["sess-001", "sess-002", "sess-003"]
}

Response:
{
  "sessions": {
    "sess-001": {...},
    "sess-002": {...},
    "sess-003": null
  }
}
```

#### 批量删除会话
```
DELETE /api/sessions/batch
Content-Type: application/json

{
  "session_ids": ["sess-001", "sess-002"]
}
```

## 目录结构

```
sessions/
├── etc/
│   └── config.yaml              # Sessions 配置文件
├── module/
│   ├── storage.py                # 存储后端抽象层
│   ├── redis_storage.py         # Redis 存储实现
│   ├── memory_storage.py        # 内存存储实现
│   ├── file_storage.py          # 文件存储实现
│   └── session_manager.py       # 会话管理器
├── service/
│   ├── cleaner.py               # 过期会话清理服务
│   └── monitor.py                # 监控服务
└── web/
    ├── manager/                  # 管理界面
    │   ├── index.html
    │   └── sessions.html         # 会话管理页面
    └── api/                      # API 文档
```

## 配置示例

### config.yaml
```yaml
sessions:
  # 存储后端配置
  storage:
    type: redis  # redis, memory, file, database
    redis:
      host: redis
      port: 6379
      db: 0
      password: ""
      cluster_mode: false
    memory:
      max_size: 10000
    file:
      path: /data/sessions
      max_files: 10000
  
  # 会话配置
  session:
    id_length: 32
    default_expires_in: 3600  # 秒
    sliding_expiration: true  # 滑动过期
    secure: true  # 仅 HTTPS
    http_only: true
  
  # 清理配置
  cleanup:
    interval: 300  # 清理间隔（秒）
    batch_size: 100  # 批量清理大小
  
  # 缓存配置
  cache:
    enabled: true
    ttl: 300  # 缓存 TTL（秒）
    max_size: 1000
```

## 非功能性需求

### 性能要求
- **高并发**：支持 10000+ QPS
- **低延迟**：读写操作延迟 < 5ms（P95）
- **高吞吐**：支持大量会话同时访问

### 可靠性要求
- **数据持久化**：会话数据不丢失（使用持久化存储时）
- **高可用**：服务可用性 > 99.9%
- **故障恢复**：存储故障时优雅降级

### 可扩展性要求
- **水平扩展**：支持多实例部署
- **存储扩展**：支持更换存储后端
- **容量扩展**：支持大规模会话存储

### 安全性要求
- **数据加密**：敏感数据加密存储（可选）
- **访问控制**：API 访问权限控制
- **安全审计**：完整的安全日志记录

## 依赖关系

### 依赖服务
- **Base 服务**：基于 base 镜像构建

### 被依赖关系
- **Gateway 服务**：用于会话验证
- **所有其他微服务**：用于会话共享

## 开发规范

### 代码规范
- 遵循 Base 服务的代码规范
- 使用类型提示
- 完整的文档字符串

### 测试要求
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- 性能测试验证高并发场景

### 文档要求
- API 文档完整
- 部署文档详细
- 运维文档清晰
