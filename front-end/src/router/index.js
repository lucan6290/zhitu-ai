import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '职途AI', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/collect',
    name: 'Collect',
    component: () => import('@/views/CollectView.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/detect',
    name: 'Detect',
    component: () => import('@/views/DetectView.vue'),
    meta: { title: '人脸识别登录', requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/chat',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - 职途AI`

  const isLoggedIn = localStorage.getItem('zhiTu_logged_in') === 'true'

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (!to.meta.requiresAuth && isLoggedIn && (to.name === 'Login' || to.name === 'Collect' || to.name === 'Detect')) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
