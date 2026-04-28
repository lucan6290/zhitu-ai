# 🤖 人脸识别智能系统

> 基于 Django + Vue.js 的前后端分离架构

## 📁 项目结构

```
agent_face_pro/
├── back-end/                    # 后端服务
│   ├── agent_face_pro/          # Django 项目配置
│   ├── myapp/                   # 主应用（视图、模型、工具）
│   ├── agent_mcp/               # MCP 服务
│   ├── system_prompt/           # AI 系统提示词
│   ├── manage.py                # Django 管理脚本
│   ├── db.sqlite3               # SQLite 数据库
│   ├── requirements.txt         # Python 依赖
│   └── README.md                # 后端说明文档
│
├── front-end/                   # 前端静态文件
│   ├── index.html               # 系统首页入口
│   ├── static/                  # 静态资源
│   │   ├── imgs/               # 人脸图像
│   │   └── js/                 # JavaScript 库
│   ├── templates/               # HTML 页面模板
│   └── README.md                # 前端说明文档
│
├── .gitignore                   # Git 忽略文件
└── PROJECT_REFACTOR.md          # 重构说明文档
```

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 进入后端目录
cd back-end

# 安装依赖
pip install -r requirements.txt

# 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 2. 访问前端

**方式一：直接打开**
- 双击 `front-end/index.html`

**方式二：使用静态服务器**
```bash
# 进入前端目录
cd front-end

# 启动 HTTP 服务器
python -m http.server 8080
```

然后访问：http://localhost:8080

## 📋 功能特性

### ✅ 人脸识别系统
- 👤 人脸信息采集与注册
- 🔍 人脸识别验证
- 🔐 账号密码登录
- 📸 实时摄像头捕获

### ✅ AI 智能体对话
- 🤖 基于 LangChain 的智能体
- 🛠️ 支持工具调用（天气查询、数据库查询）
- 💬 流式对话响应
- 📚 聊天历史本地存储

## 🔧 技术栈

### 后端
- **框架**: Django 6.0.4
- **AI**: LangChain + LangGraph + 通义千问
- **人脸识别**: face_recognition + OpenCV
- **数据库**: SQLite3 / MySQL 8.0.37
- **MCP**: FastMCP

### 前端
- **框架**: Vue.js 2.x
- **库**: jQuery
- **样式**: CSS3（响应式设计）
- **通信**: Fetch API（流式响应）

## 📖 文档

- [项目重构说明](PROJECT_REFACTOR.md) - 详细的架构和部署指南
- [后端文档](back-end/README.md) - 后端配置和使用说明
- [前端文档](front-end/README.md) - 前端配置和使用说明

## ⚙️ 配置说明

### 环境变量（back-end/myapp/env）

```env
QWEN_API_KEY="sk-your-api-key"
QWEN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL="qwen3-max-2026-01-23"
```

### 数据库配置

如需使用 MySQL，修改 `back-end/agent_face_pro/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "gzeu_sql",
        "USER": "root",
        "PASSWORD": "your-password",
        "HOST": "localhost",
        "PORT": "3306",
        "CHARSET": "utf8"
    }
}
```

## 🌐 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/face_collect/` | POST | 人脸信息采集 |
| `/face_detect/` | POST | 人脸识别匹配 |
| `/login/` | POST | 账号密码登录 |
| `/chat_agent/` | GET | AI 智能体对话（流式） |

## 🛡️ 安全建议

生产环境部署时：

1. 修改 CORS 设置为具体域名
2. 启用 CSRF 保护
3. 使用密码加密存储
4. 配置 HTTPS
5. 使用环境变量管理敏感信息

## 📝 开发说明

### 前后端分离架构

- **前端**: 纯静态文件，可部署在任何 Web 服务器
- **后端**: RESTful API 服务，支持跨域访问
- **通信**: 通过 HTTP/HTTPS 协议

### 目录说明

- `back-end/` - 包含所有后端代码和配置
- `front-end/` - 包含所有前端静态资源
- 其他文件为项目文档和配置

## 🐛 常见问题

### 1. 跨域错误
确保后端已安装 `django-cors-headers` 并正确配置

### 2. 摄像头无法使用
- 使用 HTTPS 协议
- 检查浏览器权限设置

### 3. 数据库连接失败
确保 MySQL 服务已启动且数据库 `gzeu_sql` 已创建

## 📄 许可证

保留所有原始代码版权

## 👥 维护信息

- **重构日期**: 2026-04-27
- **架构**: 前后端分离
- **版本**: 1.0.0

---

**开始使用**: 请查看 [PROJECT_REFACTOR.md](PROJECT_REFACTOR.md) 获取详细部署指南
