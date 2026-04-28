import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '智能体对话' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '账密登录' }
  },
  {
    path: '/collect',
    name: 'Collect',
    component: () => import('@/views/CollectView.vue'),
    meta: { title: '用户注册' }
  },
  {
    path: '/detect',
    name: 'Detect',
    component: () => import('@/views/DetectView.vue'),
    meta: { title: '人脸识别登录' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { title: '个人信息' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { title: '智能体对话' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - 人脸识别智能系统`
  next()
})

export default router
