# 🎯 职途AI - 岗位JD智能解析与学习路径规划助手

> 基于 Django + Vue 3 + LangGraph + MCP 的前后端分离架构

## 📖 项目简介

职途AI 是一款专为**计算机相关专业大学生**设计的智能求职辅助工具。通过AI技术自动分析招聘网站上的岗位JD（Job Description），帮助求职者快速了解目标岗位的真实技术要求，并生成个性化的学习路径规划。

### 🎯 解决的核心痛点

1. **信息不对称** - 不知道目标岗位当前真实的技术要求
2. **效率极低** - 手动整理30条JD需要1.5小时，容易遗漏高频考点
3. **优先级混乱** - 不知道先学什么后学什么，浪费时间在非核心技能上
4. **不贴合地域** - 网上通用学习路线不适合本地城市的岗位要求
5. **盲目学习** - 学了很多与目标岗位无关的技术

### 👥 目标用户

- **年龄**: 20-24岁
- **职业**: 计算机相关专业大三/大四本科生、研二研究生
- **场景**: 准备暑期实习、秋招提前批、春招补录

## 📁 项目结构

```
agent_face_pro/
├── back-end/                       # 后端服务
│   ├── apps/                       # Django应用模块
│   │   ├── face/                   # 人脸识别模块
│   │   ├── chat/                   # AI聊天模块
│   │   └── mcp/                    # MCP服务模块
│   ├── ai/                         # AI核心模块
│   │   ├── agents/                 # Agent智能体
│   │   │   └── tools/              # 工具集（数据库、天气等）
│   │   ├── mcp/                    # MCP客户端/服务端
│   │   └── prompts/                # 系统提示词
│   ├── config/                     # 项目配置
│   │   └── settings/               # 环境配置（base/development/production）
│   ├── core/                       # 核心工具
│   │   ├── utils/                  # 工具函数
│   │   └── validators/             # 验证器
│   ├── requirements/               # 依赖管理
│   │   ├── base.txt                # 基础依赖
│   │   ├── development.txt         # 开发依赖
│   │   └── production.txt          # 生产依赖
│   ├── manage.py                   # Django管理脚本
│   └── README.md                   # 后端说明文档
│
├── front-end/                      # 前端应用
│   ├── src/                        # 源代码
│   │   ├── api/                    # API接口
│   │   ├── router/                 # 路由配置
│   │   ├── stores/                 # 状态管理（Pinia）
│   │   ├── views/                  # 页面组件
│   │   │   ├── HomeView.vue        # 首页
│   │   │   ├── ChatView.vue        # AI聊天
│   │   │   ├── CollectView.vue     # 人脸采集
│   │   │   ├── DetectView.vue      # 人脸识别
│   │   │   ├── LoginView.vue       # 登录
│   │   │   └── ProfileView.vue     # 个人中心
│   │   ├── utils/                  # 工具函数
│   │   ├── App.vue                 # 根组件
│   │   └── main.js                 # 入口文件
│   ├── package.json                # 前端依赖
│   ├── vite.config.js              # Vite配置
│   └── README.md                   # 前端说明文档
│
├── docs/                           # 项目文档
│   └── 01-项目立项.md              # 项目立项文档
│
├── .gitignore                      # Git忽略文件
└── PROJECT_REFACTOR.md             # 重构说明文档
```

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 进入后端目录
cd back-end

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements/base.txt

# 配置环境变量（创建.env文件或设置系统环境变量）
# DJANGO_SECRET_KEY=your-secret-key
# QWEN_API_KEY=your-api-key
# DB_HOST=localhost
# DB_NAME=agent_face_sql
# DB_USER=root
# DB_PASSWORD=your-password

# 数据库迁移
python manage.py migrate

# 启动Django开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 2. 启动前端应用

```bash
# 进入前端目录
cd front-end

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或构建生产版本
npm run build
npm run preview
```

访问：http://localhost:5173

## 📋 核心功能（MVP阶段）

### ✅ 1. 多平台JD聚合获取
- 🔍 基于 MCP-Jobs 服务获取多平台招聘数据
- 📊 支持BOSS直聘、猎聘、智联招聘、前程无忧等平台
- 🎯 按岗位关键词、城市、数量精准筛选

### ✅ 2. 技术栈智能解析与优先级分级
- 🤖 基于通义千问qwen3-max大模型智能解析JD
- 📈 自动统计技术栈出现频率
- 🎖️ 三级优先级分级：必备 / 重要 / 加分
- 🏷️ 技术栈领域分类：后端、数据库、前端、工具、云服务等

### ✅ 3. ECharts可视化展示
- 📊 技术栈频率柱状图
- 🥧 技术领域分布饼图
- 📉 经验要求分布图
- 🎨 交互式图表，支持缩放、筛选

### ✅ 4. 基础学习路径生成
- 📚 基于用户专业背景的个性化推荐
- ⏰ 支持不同时间规划：1周 / 2周 / 1个月
- 🎯 按优先级排序的学习清单
- 💡 配套学习资源推荐

## 🔧 技术栈

### 后端
- **框架**: Django
- **AI引擎**: LangChain + LangGraph + 通义千问 qwen3-max
- **数据获取**: MCP-Jobs（多平台招聘数据聚合）
- **MCP服务**: FastMCP
- **数据库**: MySQL 8.0
- **流式响应**: SSE（Server-Sent Events）

### 前端
- **框架**: Vue 3.4
- **构建工具**: Vite 5.2
- **路由**: Vue Router 4.3
- **状态管理**: Pinia 2.1
- **样式**: CSS3（响应式设计）
- **通信**: Fetch API（流式响应）

## 📖 文档

- [项目立项文档](docs/01-项目立项.md) - 项目背景、目标用户、MVP定义
- [项目重构说明](PROJECT_REFACTOR.md) - 详细的架构和部署指南
- [后端文档](back-end/README.md) - 后端配置和使用说明
- [前端文档](front-end/README.md) - 前端配置和使用说明

## ⚙️ 配置说明

### 环境变量

创建 `.env` 文件或设置系统环境变量：

```env
# Django配置
DJANGO_SECRET_KEY=your-secret-key

# 通义千问API配置
QWEN_API_KEY=your-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-max-2026-01-23

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=agent_face_sql
DB_USER=root
DB_PASSWORD=your-password

# MCP服务配置
MCP_SERVER_URL=http://127.0.0.1:8081/mcp

# 邀请码（可选）
INVITATION_CODE=your-invitation-code
```

### 数据库配置

项目默认使用MySQL数据库，确保已创建数据库：

```sql
CREATE DATABASE agent_face_sql CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 🌐 API 接口

### 人脸识别相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/face/collect/` | POST | 人脸信息采集 |
| `/api/face/detect/` | POST | 人脸识别匹配 |
| `/api/face/login/` | POST | 账号密码登录 |
| `/api/face/profile/` | GET/POST | 用户信息管理 |

### AI聊天相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/sessions/` | GET/POST | 会话列表/创建会话 |
| `/api/chat/sessions/<id>/messages/` | GET | 获取会话消息 |
| `/api/chat/sessions/<id>/` | DELETE | 删除会话 |
| `/api/chat/agent/` | GET | AI智能体对话（SSE流式） |

### MCP服务相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/mcp/jobs/search/` | POST | 搜索岗位JD数据 |
| `/api/mcp/jobs/analyze/` | POST | 分析JD技术栈 |

## 🛡️ 安全建议

生产环境部署时：

1. **修改SECRET_KEY** - 使用强随机密钥
2. **启用HTTPS** - 配置SSL证书
3. **CORS配置** - 设置具体的允许域名
4. **CSRF保护** - 启用CSRF中间件
5. **环境变量** - 敏感信息使用环境变量管理
6. **数据库安全** - 使用强密码，限制访问权限
7. **定期备份** - 数据库定期备份

## 📝 开发说明

### 前后端分离架构

- **前端**: Vue 3 + Vite SPA应用，可部署在任何静态服务器
- **后端**: Django RESTful API服务，支持跨域访问
- **通信**: HTTP/HTTPS协议，SSE流式响应

### 开发流程

1. 用户输入「专业+目标岗位+意向城市」
2. 后端调用 MCP-Jobs 获取多平台JD数据
3. AI智能体解析技术栈并统计频率
4. 生成ECharts可视化配置
5. 通过SSE流式返回分析结果和学习路径

### 代码规范

- **后端**: 遵循Django最佳实践，应用模块化设计
- **前端**: 遵循Vue 3 Composition API风格
- **Git**: 使用语义化提交信息

## 🐛 常见问题

### 1. 跨域错误
确保后端已安装 `django-cors-headers` 并在 `INSTALLED_APPS` 和 `MIDDLEWARE` 中正确配置

### 2. 数据库连接失败
- 确保MySQL服务已启动
- 检查数据库配置信息是否正确
- 确认数据库 `agent_face_sql` 已创建

### 3. 前端启动失败
- 检查Node.js版本（推荐16+）
- 删除 `node_modules` 重新安装依赖
- 检查端口5173是否被占用

### 4. AI对话无响应
- 检查 `QWEN_API_KEY` 是否配置正确
- 查看后端日志排查错误信息
- 确认网络连接正常

### 5. MCP服务不可用
- 检查MCP服务是否启动
- 确认 `MCP_SERVER_URL` 配置正确
- 查看MCP服务日志

## 🗓️ 开发计划

### MVP阶段（当前）
- ✅ 多平台JD聚合获取
- ✅ 技术栈智能解析与优先级分级
- ✅ ECharts可视化展示
- ✅ 基础学习路径生成

### 迭代1（MVP上线后1周）
- 用户技能自评与差距分析
- 高频面试题生成

### 迭代2（上线后2周）
- 聊天历史记录保存
- 分析报告导出为PDF

### 迭代3（上线后1个月）
- 用户登录注册系统
- 岗位推荐功能
- 付费功能

## 📄 许可证

保留所有原始代码版权

## 👥 维护信息

- **项目转型日期**: 2026-04-28
- **架构**: 前后端分离 + AI智能体
- **版本**: 2.0.0

---

**开始使用**: 请查看 [项目立项文档](docs/01-项目立项.md) 了解项目背景和目标
