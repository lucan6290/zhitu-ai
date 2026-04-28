# 人脸识别智能系统 - 前端 (Vue 3)

> 基于 Vue 3 + Vite + Pinia 的现代化前端应用

## 🚀 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.4.21 | 渐进式 JavaScript 框架 |
| Vite | 5.2.0 | 下一代前端构建工具 |
| Vue Router | 4.3.0 | Vue.js 官方路由 |
| Pinia | 2.1.7 | Vue.js 状态管理库 |

## 📁 项目结构

```
front-end/
├── src/
│   ├── views/                    # 页面组件
│   │   ├── HomeView.vue         # 首页
│   │   ├── LoginView.vue        # 账密登录
│   │   ├── CollectView.vue      # 人脸采集注册
│   │   ├── DetectView.vue       # 人脸识别登录
│   │   └── ChatView.vue         # AI 智能体对话
│   ├── components/              # 可复用组件
│   ├── router/
│   │   └── index.js             # 路由配置
│   ├── stores/
│   │   └── index.js             # Pinia 状态管理
│   ├── api/
│   │   └── index.js             # API 接口封装
│   ├── utils/
│   │   └── faceUtil.js          # 摄像头工具函数
│   ├── assets/
│   │   └── main.css             # 全局样式
│   ├── App.vue                  # 根组件
│   └── main.js                  # 入口文件
├── public/                      # 静态资源
├── index.html                   # HTML 入口
├── vite.config.js               # Vite 配置
└── package.json                 # 项目配置
```

## 🎯 功能特性

### 1. 人脸采集注册 (`/collect`)
- 📷 实时摄像头捕获
- 📝 表单验证（姓名、年龄、电话、密码）
- ✅ 人脸检测和重复注册检查
- 💾 用户信息保存

### 2. 人脸识别登录 (`/detect`)
- 🔍 摄像头实时捕获
- 🎭 人脸比对验证
- 🔐 自动登录

### 3. 账号密码登录 (`/login`)
- 📱 手机号 + 密码登录
- ✅ 表单验证
- ❌ 错误提示

### 4. AI 智能体对话 (`/chat`)
- 💬 流式对话响应
- 📚 历史会话管理
- 💾 本地存储持久化
- 🤖 AI 工具调用支持

## 🛠️ 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问: http://localhost:3000

### 生产构建

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/face_collect/` | POST | 人脸信息采集 |
| `/face_detect/` | POST | 人脸识别匹配 |
| `/login/` | POST | 账号密码登录 |
| `/chat_agent/` | GET | AI 智能体对话（流式） |

## 🔧 配置说明

### Vite 开发服务器代理

```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### API 基础 URL

修改 `src/api/index.js`:

```javascript
const BASE_URL = 'http://localhost:8000'
```

## 📦 核心依赖

```json
{
  "dependencies": {
    "vue": "^3.4.21",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.4",
    "vite": "^5.2.0"
  }
}
```

## 🎨 样式特性

- ✅ 响应式设计（支持移动端）
- ✅ 渐变背景和动画效果
- ✅ 现代化 UI 设计
- ✅ 深色模式预留

## 🔐 功能亮点

### 1. 摄像头工具 (Composition API)

```javascript
import { useCamera } from '@/utils/faceUtil'

const { isOpen, openCamera, getFrameAsBase64 } = useCamera({
  width: 500,
  height: 600
})
```

### 2. 流式对话

```javascript
const response = await chatAgent(question)
const reader = response.body.getReader()
const decoder = new TextDecoder('utf-8')

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const text = decoder.decode(value, { stream: true })
  // 实时更新 UI
}
```

### 3. Pinia 状态管理

```javascript
import { useChatStore } from '@/stores'

const chatStore = useChatStore()
chatStore.addMessage({ name: '用户', text: '你好' })
chatStore.saveCurrentSession()
```

## 🌐 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 📝 开发注意事项

1. **摄像头权限**: 需要用户授权摄像头权限
2. **HTTPS 要求**: 生产环境建议使用 HTTPS
3. **跨域配置**: 确保后端已配置 CORS
4. **API 地址**: 开发环境使用代理，生产环境修改 BASE_URL

## 🚀 部署建议

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/front-end/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📄 许可证

保留所有原始代码版权

---

**技术栈**: Vue 3 + Vite + Vue Router + Pinia  
**构建工具**: Vite 5.x  
**开发服务器**: http://localhost:3000
