# AI Node 服务需求设计文档

## 服务概述

AI Node 是平台的 AI 服务节点，负责 AI 相关的服务，包括对接 AI 模型、MCP（Model Context Protocol）服务等。该服务提供统一的 AI 能力接口，支持多种 AI 模型和服务的集成。

## 核心定位

- **AI 能力提供**：为平台提供统一的 AI 能力接口
- **模型对接**：支持对接多种 AI 模型（OpenAI、Claude、本地模型等）
- **MCP 服务**：支持 MCP（Model Context Protocol）服务
- **AI 应用**：支持构建基于 AI 的应用和服务

## 技术栈

- **Web 框架**：基于 Base 服务（FastAPI）
- **部署方式**：Docker 镜像（基于 base 镜像）
- **AI 框架**：支持多种 AI SDK（OpenAI、Anthropic 等）
- **协议支持**：HTTP、WebSocket、gRPC（可选）

## 核心功能需求

### 1. AI 模型对接

#### 1.1 支持的模型类型
- **OpenAI 模型**：
  - GPT-3.5、GPT-4 系列
  - Embeddings 模型
  - 图像生成模型（DALL-E）
  - 语音模型（Whisper、TTS）
- **Anthropic 模型**：
  - Claude 系列模型
- **本地模型**：
  - 支持本地部署的模型（Ollama、vLLM 等）
  - 支持自定义模型接口
- **其他模型**：
  - Google Gemini
  - 百度文心一言
  - 阿里通义千问
  - 其他兼容 OpenAI API 的模型

#### 1.2 模型配置管理
- **配置方式**：支持通过配置文件或管理界面配置模型
- **配置内容**：
  - 模型标识（唯一 ID）
  - 模型类型（OpenAI、Anthropic、Local 等）
  - API 地址和密钥
  - 模型参数（temperature、max_tokens 等）
  - 模型能力（文本生成、图像生成、语音等）
- **多模型支持**：支持同时配置多个模型
- **模型切换**：支持运行时切换模型

#### 1.3 模型调用
- **统一接口**：提供统一的模型调用接口
- **参数映射**：将统一参数映射到不同模型的特定参数
- **错误处理**：统一的错误处理和重试机制
- **限流控制**：支持模型级别的限流控制

### 2. 文本生成服务

#### 2.1 聊天对话
- **接口**：`POST /api/ai/chat`
- **功能**：
  - 支持多轮对话
  - 支持系统提示词（System Prompt）
  - 支持流式输出（Server-Sent Events）
  - 支持函数调用（Function Calling）
- **参数**：
  - `model`：模型 ID
  - `messages`：对话消息列表
  - `temperature`：温度参数
  - `max_tokens`：最大 token 数
  - `stream`：是否流式输出
- **返回**：生成的文本或流式数据

#### 2.2 文本补全
- **接口**：`POST /api/ai/completion`
- **功能**：
  - 单次文本补全
  - 支持提示词模板
- **参数**：
  - `model`：模型 ID
  - `prompt`：提示词
  - `temperature`：温度参数
  - `max_tokens`：最大 token 数
- **返回**：补全的文本

#### 2.3 文本嵌入
- **接口**：`POST /api/ai/embeddings`
- **功能**：
  - 文本向量化
  - 支持批量处理
- **参数**：
  - `model`：嵌入模型 ID
  - `texts`：文本列表（支持单个或多个）
- **返回**：向量数组

### 3. 图像生成服务

#### 3.1 图像生成
- **接口**：`POST /api/ai/images/generate`
- **功能**：
  - 根据文本提示生成图像
  - 支持多种图像尺寸
  - 支持图像风格设置
- **参数**：
  - `model`：图像生成模型 ID
  - `prompt`：文本提示
  - `size`：图像尺寸（可选）
  - `style`：图像风格（可选）
  - `n`：生成数量（可选）
- **返回**：图像 URL 或 Base64 编码

#### 3.2 图像编辑
- **接口**：`POST /api/ai/images/edit`
- **功能**：
  - 图像编辑和修改
  - 支持图像修复
- **参数**：
  - `model`：图像编辑模型 ID
  - `image`：原始图像
  - `mask`：遮罩图像（可选）
  - `prompt`：编辑提示
- **返回**：编辑后的图像

#### 3.3 图像变体
- **接口**：`POST /api/ai/images/variations`
- **功能**：
  - 生成图像的变体
- **参数**：
  - `model`：图像模型 ID
  - `image`：原始图像
  - `n`：变体数量（可选）
- **返回**：变体图像列表

### 4. 语音服务

#### 4.1 语音转文本（STT）
- **接口**：`POST /api/ai/audio/transcribe`
- **功能**：
  - 将音频文件转换为文本
  - 支持多种音频格式
  - 支持多语言识别
- **参数**：
  - `model`：语音识别模型 ID
  - `audio`：音频文件
  - `language`：语言代码（可选）
  - `prompt`：提示文本（可选）
- **返回**：识别的文本

#### 4.2 文本转语音（TTS）
- **接口**：`POST /api/ai/audio/synthesize`
- **功能**：
  - 将文本转换为语音
  - 支持多种语音风格
  - 支持多种音频格式
- **参数**：
  - `model`：语音合成模型 ID
  - `text`：要合成的文本
  - `voice`：语音风格（可选）
  - `format`：音频格式（可选）
- **返回**：音频文件或流

### 5. MCP 服务支持

#### 5.1 MCP 协议支持
- **协议定义**：支持 Model Context Protocol 标准
- **服务注册**：支持 MCP 服务的注册和发现
- **服务调用**：支持调用已注册的 MCP 服务

#### 5.2 MCP 服务管理
- **服务配置**：
  - MCP 服务地址和端口
  - 服务能力描述
  - 服务认证信息
- **服务发现**：
  - 自动发现可用的 MCP 服务
  - 服务健康检查
- **服务调用**：
  - 统一的 MCP 服务调用接口
  - 支持同步和异步调用

#### 5.3 MCP 工具集成
- **工具注册**：支持注册 MCP 工具
- **工具调用**：在 AI 对话中调用 MCP 工具
- **工具管理**：提供工具的管理界面

### 6. 提示词管理

#### 6.1 提示词模板
- **模板创建**：支持创建提示词模板
- **模板变量**：支持模板变量替换
- **模板分类**：支持模板分类管理
- **模板共享**：支持模板共享和复用

#### 6.2 提示词优化
- **提示词库**：维护常用提示词库
- **提示词建议**：根据场景推荐提示词
- **提示词评估**：评估提示词效果

### 7. 对话管理

#### 7.1 对话历史
- **历史存储**：存储对话历史记录
- **历史查询**：支持查询历史对话
- **历史导出**：支持导出对话历史

#### 7.2 对话上下文
- **上下文管理**：管理对话上下文
- **上下文窗口**：控制上下文窗口大小
- **上下文压缩**：支持上下文压缩（可选）

### 8. 流式输出

#### 8.1 Server-Sent Events (SSE)
- **流式接口**：支持 SSE 流式输出
- **事件类型**：支持多种事件类型
  - `message`：消息内容
  - `done`：完成事件
  - `error`：错误事件
- **断线重连**：支持断线重连机制

#### 8.2 WebSocket 支持
- **WebSocket 接口**：支持 WebSocket 实时通信
- **消息格式**：定义标准的消息格式
- **连接管理**：管理 WebSocket 连接

### 9. 成本与使用统计

#### 9.1 使用统计
- **调用统计**：
  - 调用次数
  - Token 使用量
  - 调用耗时
  - 成功率
- **按模型统计**：按模型维度统计使用情况
- **按用户统计**：按用户维度统计使用情况

#### 9.2 成本计算
- **Token 计费**：根据 Token 使用量计算成本
- **模型定价**：支持配置不同模型的定价
- **成本报表**：生成成本使用报表

### 10. 缓存与优化

#### 10.1 响应缓存
- **缓存策略**：缓存相同提示词的响应
- **缓存失效**：支持缓存失效策略
- **缓存管理**：提供缓存管理界面

#### 10.2 请求优化
- **请求合并**：合并相似的请求
- **批量处理**：支持批量处理请求
- **异步处理**：支持异步处理长时间任务

## API 接口设计

### 文本生成 API

#### 聊天对话
```
POST /api/ai/chat
Content-Type: application/json

{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}

Response:
{
  "id": "chat-001",
  "model": "gpt-4",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

#### 流式聊天
```
POST /api/ai/chat
Content-Type: application/json

{
  "model": "gpt-4",
  "messages": [...],
  "stream": true
}

Response (SSE):
data: {"id": "chat-001", "choices": [{"delta": {"content": "Hello"}}]}

data: {"id": "chat-001", "choices": [{"delta": {"content": "!"}}]}

data: [DONE]
```

### 图像生成 API

#### 生成图像
```
POST /api/ai/images/generate
Content-Type: application/json

{
  "model": "dall-e-3",
  "prompt": "A beautiful sunset over the ocean",
  "size": "1024x1024",
  "n": 1
}

Response:
{
  "images": [
    {
      "url": "https://...",
      "revised_prompt": "..."
    }
  ]
}
```

### 语音服务 API

#### 语音转文本
```
POST /api/ai/audio/transcribe
Content-Type: multipart/form-data

{
  "model": "whisper-1",
  "audio": <file>,
  "language": "zh"
}

Response:
{
  "text": "转录的文本内容"
}
```

### MCP 服务 API

#### 调用 MCP 服务
```
POST /api/ai/mcp/{service_name}/call
Content-Type: application/json

{
  "method": "method_name",
  "params": {...}
}

Response:
{
  "result": {...}
}
```

### 模型管理 API

#### 获取模型列表
```
GET /api/ai/models

Response:
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "type": "openai",
      "capabilities": ["chat", "completion"],
      "status": "active"
    }
  ]
}
```

#### 获取模型详情
```
GET /api/ai/models/{model_id}

Response:
{
  "id": "gpt-4",
  "name": "GPT-4",
  "type": "openai",
  "config": {...},
  "stats": {
    "total_calls": 1000,
    "total_tokens": 100000
  }
}
```

### 使用统计 API

#### 获取使用统计
```
GET /api/ai/stats?model=gpt-4&start_date=2024-01-01&end_date=2024-01-31

Response:
{
  "total_calls": 1000,
  "total_tokens": 100000,
  "total_cost": 10.5,
  "by_model": {...},
  "by_date": [...]
}
```

## 目录结构

```
ai_node/
├── etc/
│   └── config.yaml              # AI Node 配置文件
├── module/
│   ├── model_adapter.py         # 模型适配器抽象层
│   ├── openai_adapter.py        # OpenAI 适配器
│   ├── anthropic_adapter.py     # Anthropic 适配器
│   ├── local_adapter.py         # 本地模型适配器
│   ├── mcp_client.py            # MCP 客户端
│   └── prompt_manager.py        # 提示词管理器
├── service/
│   ├── model_manager.py         # 模型管理服务
│   ├── cache_service.py         # 缓存服务
│   └── stats_service.py         # 统计服务
└── web/
    ├── manager/                 # 管理界面
    │   ├── index.html
    │   ├── models.html          # 模型管理页面
    │   ├── prompts.html         # 提示词管理页面
    │   └── stats.html           # 统计页面
    └── api/                     # API 文档
```

## 配置示例

### config.yaml
```yaml
ai_node:
  # 模型配置
  models:
    - id: gpt-4
      name: GPT-4
      type: openai
      api_key: ${OPENAI_API_KEY}
      api_base: https://api.openai.com/v1
      capabilities: [chat, completion, embeddings]
      default_params:
        temperature: 0.7
        max_tokens: 2000
    
    - id: claude-3
      name: Claude 3
      type: anthropic
      api_key: ${ANTHROPIC_API_KEY}
      capabilities: [chat, completion]
  
    - id: local-llm
      name: Local LLM
      type: local
      api_base: http://localhost:8000/v1
      capabilities: [chat, completion]
  
  # MCP 服务配置
  mcp:
    services:
      - name: file_manager
        address: http://mcp-file:8000
        capabilities: [read_file, write_file]
  
  # 缓存配置
  cache:
    enabled: true
    ttl: 3600
    max_size: 1000
  
  # 限流配置
  rate_limit:
    enabled: true
    per_minute: 60
    per_hour: 1000
```

## 非功能性需求

### 性能要求
- **低延迟**：API 响应时间 < 2s（P95，不含模型生成时间）
- **高并发**：支持 100+ 并发请求
- **流式输出**：流式输出延迟 < 100ms

### 可靠性要求
- **错误处理**：完善的错误处理和重试机制
- **降级策略**：模型不可用时优雅降级
- **高可用**：服务可用性 > 99.5%

### 可扩展性要求
- **模型扩展**：支持轻松添加新模型
- **协议扩展**：支持新协议接入
- **水平扩展**：支持多实例部署

### 安全性要求
- **API 密钥管理**：安全的 API 密钥存储和管理
- **访问控制**：API 访问权限控制
- **数据隐私**：用户数据隐私保护

## 依赖关系

### 依赖服务
- **Base 服务**：基于 base 镜像构建
- **Gateway 服务**：通过 Gateway 对外提供服务

### 外部依赖
- **AI 模型服务**：OpenAI、Anthropic 等外部 AI 服务
- **MCP 服务**：外部 MCP 服务（可选）

### 被依赖关系
- 其他服务可通过 AI Node 使用 AI 能力

## 开发规范

### 代码规范
- 遵循 Base 服务的代码规范
- 使用类型提示
- 完整的文档字符串

### 测试要求
- 单元测试覆盖率 > 70%
- 集成测试覆盖主要功能
- Mock 测试覆盖外部 API 调用

### 文档要求
- API 文档完整
- 模型配置文档详细
- 使用示例清晰
