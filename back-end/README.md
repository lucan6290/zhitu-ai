# 人脸识别智能系统 - 后端服务

## 项目概述

本项目是一个基于 Django 的人脸识别智能系统后端服务，采用前后端分离架构，集成了人脸识别、智能对话、MCP工具调用等功能。系统支持用户注册登录（密码/人脸识别）、AI智能对话、职位查询与投递等核心功能。

## 项目架构

本项目采用**前后端分离**架构：

- **后端**: Django REST API (当前目录)
- **前端**: Vue.js (`../front-end/`)

### 核心特性

- 🔐 **双重认证**: 支持密码登录和人脸识别登录
- 🤖 **AI智能对话**: 基于通义千问的智能对话系统
- 🛠️ **MCP工具集成**: 支持职位查询和投递功能
- 💾 **会话管理**: 完整的聊天会话历史记录
- 🎯 **人脸识别**: 基于 face_recognition 的高精度人脸识别

## 项目结构

```
back-end/
├── config/                     # 项目配置
│   ├── settings/              # 分环境配置
│   │   ├── __init__.py       # 环境选择器
│   │   ├── base.py           # 基础配置
│   │   ├── development.py    # 开发环境
│   │   └── production.py     # 生产环境
│   ├── urls.py               # 主路由配置
│   ├── wsgi.py               # WSGI应用入口
│   └── asgi.py               # ASGI应用入口
│
├── apps/                       # Django应用模块
│   ├── face/                  # 人脸识别模块
│   │   ├── views.py           # 认证视图（注册/登录/登出）
│   │   ├── views_profile.py   # 用户信息视图
│   │   ├── models.py          # 用户信息模型
│   │   ├── urls.py            # 路由配置
│   │   ├── forms.py           # 表单验证
│   │   ├── services.py        # 业务逻辑层
│   │   └── tests/             # 单元测试
│   │
│   ├── chat/                  # 智能对话模块
│   │   ├── views.py           # 会话和消息视图
│   │   ├── models.py          # 会话和消息模型
│   │   ├── urls.py            # 路由配置
│   │   └── tests/             # 单元测试
│   │
│   └── mcp/                   # MCP工具模块
│       ├── views.py           # 职位查询和投递视图
│       ├── models.py          # 职位缓存模型
│       ├── urls.py            # 路由配置
│       └── tests/             # 单元测试
│
├── ai/                         # AI模块
│   ├── agents/                # Agent相关
│   │   ├── loader.py          # LLM加载器
│   │   └── tools/             # Agent工具
│   │       └── database.py    # 数据库查询工具
│   ├── mcp/                   # MCP服务
│   │   ├── client.py          # MCP客户端
│   │   └── server.py          # MCP服务器
│   └── prompts/               # 系统提示词
│       └── system_prompt.py   # AI系统提示词
│
├── core/                       # 核心模块
│   ├── utils/                 # 工具函数
│   │   ├── image_utils.py     # 图像处理工具
│   │   ├── random_utils.py    # 随机数生成工具
│   │   ├── data_utils.py      # 数据处理工具
│   │   └── response.py        # API响应工具
│   ├── validators/            # 验证器
│   │   └── form_validators.py # 表单验证器
│   └── exceptions.py          # 自定义异常
│
├── tests/                      # 项目级测试
│   ├── test_face.py           # 人脸识别测试
│   └── test_chat.py           # 对话功能测试
│
├── media/                      # 媒体文件目录
│   └── face_images/           # 人脸图像存储
│
├── requirements/               # 依赖配置
│   ├── base.txt               # 基础依赖
│   ├── development.txt        # 开发环境依赖
│   └── production.txt         # 生产环境依赖
│
├── manage.py                   # Django管理脚本
├── .env                        # 环境变量配置
├── .env.example               # 环境变量示例
└── README.md                   # 项目文档
```

## 技术栈

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web框架 | Django | 6.0.4 | Python Web框架 |
| AI框架 | LangChain | - | LLM应用开发框架 |
| AI框架 | LangGraph | - | Agent工作流框架 |
| LLM | 通义千问 | qwen3-max | 阿里云大语言模型 |
| 人脸识别 | face_recognition | - | 人脸识别库 |
| 图像处理 | OpenCV | - | 计算机视觉库 |
| 数据库 | MySQL | 8.0.37 | 关系型数据库 |
| 工具协议 | MCP | FastMCP | Model Context Protocol |
| 跨域处理 | django-cors-headers | - | CORS中间件 |

## 环境要求

- Python 3.10+
- MySQL 8.0+
- Node.js 16+ (用于MCP服务)

## 快速开始

### 1. 克隆项目

```bash
cd back-end
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements/development.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Django配置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ENV=development

# 通义千问API配置
QWEN_API_KEY=your-api-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-max-2026-01-23

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=agent_face_sql

# MCP服务配置
MCP_SERVER_URL=http://127.0.0.1:8081/mcp

# 邀请码（用于注册）
INVITATION_CODE=your-invitation-code

# 生产环境配置（可选）
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 5. 创建数据库

```sql
CREATE DATABASE agent_face_sql CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 运行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

服务将在 `http://localhost:8000` 启动。

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: Session-based Authentication
- **响应格式**: JSON

### 统一响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {}
}
```

### 1. 人脸识别模块 (`/api/v1/`)

#### 1.1 用户注册

**接口**: `POST /api/v1/auth/register/`

**请求参数**:
```json
{
  "user_name": "string",
  "user_pwd": "string",
  "user_age": 0,
  "user_phone": "string",
  "invitation_code": "string",
  "face_image": "string (base64, 可选)"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": 123
  }
}
```

**错误码**:
- `1001`: 邀请码无效
- `1002`: 用户名已存在
- `1003`: 密码格式错误
- `400`: 参数错误

#### 1.2 密码登录

**接口**: `POST /api/v1/auth/login/password/`

**请求参数**:
```json
{
  "login_account": "string (用户名或手机号)",
  "user_pwd": "string"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": 123,
    "user_name": "张三",
    "user_age": 25,
    "user_phone": "13800138000"
  }
}
```

**错误码**:
- `1004`: 登录账号或密码错误

#### 1.3 人脸识别登录

**接口**: `POST /api/v1/auth/login/face/`

**请求参数**:
```json
{
  "face_image": "string (base64)"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": 123,
    "user_name": "张三",
    "user_age": 25,
    "user_phone": "13800138000"
  }
}
```

**错误码**:
- `1005`: 未识别到已注册人脸

#### 1.4 用户登出

**接口**: `POST /api/v1/auth/logout/`

**响应示例**:
```json
{
  "code": 0,
  "msg": "success"
}
```

#### 1.5 获取用户信息

**接口**: `GET /api/v1/user/profile/`

**需要认证**: 是

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": 123,
    "user_name": "张三",
    "user_age": 25,
    "user_phone": "13800138000",
    "created_at": "2024-01-01 12:00:00"
  }
}
```

### 2. 智能对话模块 (`/api/v1/chat/`)

#### 2.1 获取会话列表

**接口**: `GET /api/v1/chat/sessions/`

**需要认证**: 是

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "sessions": [
      {
        "session_id": 1,
        "title": "新会话",
        "last_message_time": "2024-01-01 12:00:00"
      }
    ]
  }
}
```

#### 2.2 创建新会话

**接口**: `POST /api/v1/chat/sessions/`

**需要认证**: 是

**请求参数**:
```json
{
  "title": "string (可选)"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "session_id": 1,
    "title": "新会话"
  }
}
```

#### 2.3 获取会话消息

**接口**: `GET /api/v1/chat/sessions/{session_id}/messages/`

**需要认证**: 是

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "messages": [
      {
        "message_id": 1,
        "role": "user",
        "content": "你好",
        "thinking_process": null,
        "echarts_config": null,
        "created_at": "2024-01-01 12:00:00"
      },
      {
        "message_id": 2,
        "role": "assistant",
        "content": "你好！有什么可以帮助你的吗？",
        "thinking_process": null,
        "echarts_config": null,
        "created_at": "2024-01-01 12:00:01"
      }
    ]
  }
}
```

**错误码**:
- `2001`: 会话不存在
- `2002`: 无权访问该会话

#### 2.4 删除会话

**接口**: `DELETE /api/v1/chat/sessions/{session_id}/`

**需要认证**: 是

**响应示例**:
```json
{
  "code": 0,
  "msg": "success"
}
```

#### 2.5 AI智能对话 (SSE流式响应)

**接口**: `GET /api/v1/chat/agent/`

**需要认证**: 是

**请求参数**:
- `session_id`: 会话ID (必需)
- `content`: 对话内容 (必需)
- `deep_thinking`: 是否深度思考 (可选, 默认false)

**响应格式**: Server-Sent Events (SSE)

**事件类型**:
- `content`: 内容片段
- `end`: 对话结束
- `error`: 错误信息

**示例**:
```
event: content
data: 你好

event: content
data: ！

event: end
```

### 3. MCP工具模块 (`/api/v1/mcp/`)

#### 3.1 查询职位列表

**接口**: `GET /api/v1/mcp/jobs/`

**需要认证**: 是

**请求参数**:
- `keyword`: 职位关键词 (可选)
- `city`: 城市 (可选)
- `recruit_type`: 职位类型 (可选)
- `limit`: 返回数量限制 (可选, 默认20)

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "jobs": [
      {
        "job_title": "Python开发工程师",
        "company": "某科技公司",
        "salary": "15k-25k",
        "location": "北京"
      }
    ],
    "from_cache": true
  }
}
```

**错误码**:
- `3001`: MCP服务暂时不可用

#### 3.2 投递职位

**接口**: `POST /api/v1/mcp/jobs/apply/`

**需要认证**: 是

**请求参数**:
```json
{
  "work_pin": "string (职位标识)"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "result": "投递成功"
  }
}
```

## 数据库模型

### 1. UserInfo (用户信息)

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | AutoField | 用户ID (主键) |
| user_name | CharField(100) | 用户名 (唯一) |
| user_age | IntegerField | 用户年龄 |
| user_phone | CharField(20) | 手机号码 (索引) |
| user_pwd | CharField(100) | 用户密码 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### 2. ChatSession (聊天会话)

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | BigAutoField | 会话ID (主键) |
| user_id | IntegerField | 用户ID |
| title | CharField(200) | 会话标题 |
| last_message_time | DateTimeField | 最后消息时间 |
| created_at | DateTimeField | 创建时间 |

### 3. ChatMessage (聊天消息)

| 字段 | 类型 | 说明 |
|------|------|------|
| message_id | BigAutoField | 消息ID (主键) |
| session | ForeignKey | 所属会话 |
| role | CharField(20) | 角色 (user/assistant) |
| content | TextField | 消息内容 |
| thinking_process | TextField | 思考过程 (可选) |
| echarts_config | JSONField | ECharts配置 (可选) |
| created_at | DateTimeField | 创建时间 |

### 4. MCPJobsCache (职位缓存)

| 字段 | 类型 | 说明 |
|------|------|------|
| cache_id | BigAutoField | 缓存ID (主键) |
| keyword | CharField(200) | 岗位关键词 |
| city | CharField(100) | 城市 |
| recruit_type | IntegerField | 职位类型 |
| jobs_data | JSONField | 职位数据 |
| expire_at | DateTimeField | 过期时间 |
| created_at | DateTimeField | 创建时间 |

## 配置说明

### 环境配置

项目支持三种环境配置：

1. **development** (开发环境) - 默认
   - DEBUG = True
   - 允许所有主机访问
   - CORS允许所有来源
   - 控制台日志输出

2. **production** (生产环境)
   - DEBUG = False
   - 需要配置 ALLOWED_HOSTS
   - 需要配置 CORS_ALLOWED_ORIGINS
   - HTTPS安全配置
   - 文件日志输出

### 切换环境

修改 `.env` 文件中的 `DJANGO_ENV`:

```env
DJANGO_ENV=development  # 开发环境
# 或
DJANGO_ENV=production   # 生产环境
```

### 关键配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DJANGO_SECRET_KEY | Django密钥 | - |
| DJANGO_ENV | 运行环境 | development |
| QWEN_API_KEY | 通义千问API密钥 | - |
| QWEN_BASE_URL | 通义千问API地址 | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| QWEN_MODEL | 使用的模型 | qwen3-max-2026-01-23 |
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 3306 |
| DB_USER | 数据库用户 | root |
| DB_PASSWORD | 数据库密码 | 123456 |
| DB_NAME | 数据库名称 | agent_face_sql |
| INVITATION_CODE | 注册邀请码 | - |

## 运行测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用的测试
python manage.py test apps.face
python manage.py test apps.chat

# 运行特定测试文件
python manage.py test apps.face.tests.test_views
```

## 常见问题与解决方案

### 1. 数据库连接失败

**问题**: `Can't connect to MySQL server`

**解决方案**:
- 检查MySQL服务是否启动
- 确认数据库配置正确 (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)
- 确认数据库已创建: `CREATE DATABASE agent_face_sql CHARACTER SET utf8mb4;`
- 检查用户权限

### 2. 人脸识别库安装失败

**问题**: `face_recognition` 安装失败

**解决方案**:
- Windows: 需要安装 Visual Studio Build Tools
- Linux: 安装依赖 `sudo apt-get install cmake`
- Mac: 安装依赖 `brew install cmake`

### 3. CORS跨域问题

**问题**: 前端请求时出现CORS错误

**解决方案**:
- 开发环境: `CORS_ALLOW_ALL_ORIGINS = True` (已配置)
- 生产环境: 在 `.env` 中配置 `CORS_ALLOWED_ORIGINS`

### 4. Session认证失败

**问题**: API返回 401 未登录

**解决方案**:
- 确保前端请求时携带 credentials: `fetch(url, { credentials: 'include' })`
- 检查Session中间件配置
- 确认已调用登录接口

### 5. MCP服务连接失败

**问题**: 职位查询返回 "MCP服务暂时不可用"

**解决方案**:
- 检查MCP服务是否启动
- 确认 MCP_SERVER_URL 配置正确
- 检查网络连接

### 6. 通义千问API调用失败

**问题**: AI对话无响应或报错

**解决方案**:
- 检查 QWEN_API_KEY 是否正确
- 确认API配额是否充足
- 检查网络连接到阿里云服务

### 7. 人脸识别准确率低

**问题**: 人脸登录识别失败

**解决方案**:
- 确保注册时人脸图像清晰
- 光线充足，正面拍摄
- 检查图像质量，避免模糊或遮挡

## 开发指南

### 代码规范

- 遵循 PEP 8 编码规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 保持代码简洁和可读性

### 分支管理

- `main`: 主分支，生产环境代码
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 提交规范

使用语义化提交信息：

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

## 性能优化建议

1. **数据库优化**
   - 为常用查询字段添加索引
   - 使用 select_related 和 prefetch_related 减少查询次数
   - 定期清理过期数据

2. **缓存策略**
   - 使用 Redis 缓存热点数据
   - MCP职位数据已实现缓存机制
   - 考虑缓存用户会话信息

3. **异步处理**
   - 使用 Celery 处理耗时任务
   - AI对话采用异步流式响应

## 安全建议

1. **生产环境必须配置**:
   - 设置强密码的 DJANGO_SECRET_KEY
   - 配置 ALLOWED_HOSTS
   - 启用 HTTPS
   - 配置 CORS_ALLOWED_ORIGINS

2. **数据安全**:
   - 密码加密存储
   - 敏感信息不要提交到版本控制
   - 定期备份数据库

3. **API安全**:
   - 实施请求频率限制
   - 验证所有输入参数
   - 记录异常请求日志

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✨ 实现用户注册登录功能（密码/人脸识别）
- ✨ 集成通义千问AI对话
- ✨ 实现MCP职位查询和投递功能
- ✨ 完善会话管理功能
- 📝 完善API文档

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交 Issue。
