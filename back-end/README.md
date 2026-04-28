# 人脸识别智能系统 - 后端服务

## 项目架构

本项目采用**前后端分离**架构：

- **后端**: Django REST API (当前目录)
- **前端**: Vue.js (`../front-end/`)

## 项目结构

```
back-end/
├── config/                     # 项目配置
│   ├── settings/              # 分环境配置
│   │   ├── base.py           # 基础配置
│   │   ├── development.py    # 开发环境
│   │   └── production.py     # 生产环境
│   ├── urls.py               # 主路由
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                       # Django应用
│   ├── face/                  # 人脸识别API
│   │   ├── views.py           # 视图层
│   │   ├── models.py          # 数据模型
│   │   ├── urls.py            # 路由
│   │   ├── forms.py           # 表单验证
│   │   ├── services.py        # 业务逻辑
│   │   └── tests/             # 单元测试
│   └── chat/                  # 智能对话API
│       ├── views.py
│       ├── models.py
│       ├── urls.py
│       └── tests/
│
├── ai/                         # AI模块
│   ├── agents/                # Agent加载器
│   │   ├── loader.py
│   │   └── tools/             # 工具定义
│   ├── mcp/                   # MCP服务
│   │   ├── client.py
│   │   └── server.py
│   └── prompts/               # 系统提示词
│       └── system_prompt.py
│
├── core/                       # 核心模块
│   ├── utils/                 # 工具函数
│   │   ├── image_utils.py
│   │   ├── random_utils.py
│   │   └── data_utils.py
│   ├── validators/            # 验证器
│   │   └── form_validators.py
│   └── exceptions.py          # 自定义异常
│
├── tests/                      # 项目级测试
│   ├── test_face.py
│   └── test_chat.py
│
├── crawlers/                   # 爬虫脚本
│   ├── douban.py
│   ├── msn_sports.py
│   └── national_stats.py
│
├── media/                      # 媒体文件
│   └── face_images/           # 人脸图像
│
├── requirements/               # 依赖配置
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── manage.py
├── .env
├── .env.example
└── README.md
```

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | Django 6.0.4 |
| AI框架 | LangChain + LangGraph |
| LLM | 通义千问 (qwen3-max) |
| 人脸识别 | face_recognition + OpenCV |
| 数据库 | SQLite3 / MySQL 8.0.37 |
| 工具协议 | MCP (FastMCP) |

## 安装依赖

```bash
pip install -r requirements/development.txt
```

## 配置说明

复制 `.env.example` 为 `.env` 并配置环境变量：

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ENV=development

QWEN_API_KEY=your-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-max-2026-01-23

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=gzeu_sql

MCP_SERVER_URL=http://127.0.0.1:8081/mcp
```

## 启动服务

```bash
# 启动 Django 后端
python manage.py runserver 0.0.0.0:8000

# 启动 MCP 服务器（可选）
python -m ai.mcp.server
```

## API 接口

### 人脸识别接口 (`/api/face/`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/face/collect/` | POST | 人脸信息采集 |
| `/api/face/detect/` | POST | 人脸识别匹配 |
| `/api/face/login/` | POST | 用户登录 |

### 智能对话接口 (`/api/chat/`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/stream/` | GET | 流式响应测试 |
| `/api/chat/stream_llm/` | GET | LLM流式对话 |
| `/api/chat/agent/` | GET | AI智能体对话 |

## 运行测试

```bash
python manage.py test
```

## 目录说明

| 目录 | 说明 |
|------|------|
| `config/` | Django项目配置 |
| `apps/` | Django应用（face/chat） |
| `ai/` | AI相关模块（Agent/MCP/Prompts） |
| `core/` | 核心工具和异常 |
| `tests/` | 项目级测试 |
| `crawlers/` | 数据爬虫脚本 |
| `media/` | 用户上传的媒体文件 |
