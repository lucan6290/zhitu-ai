<template>
  <div class="login-page">
    <div class="login-container">
      <div class="brand">职途AI</div>
      <p class="brand-desc">岗位JD智能解析与学习路径规划助手</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>账号</label>
          <input
            type="text"
            v-model="loginAccount"
            placeholder="请输入用户名或手机号"
            required
          >
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            type="password"
            v-model="password"
            placeholder="6-20 位，英文加数字"
            required
          >
        </div>

        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <div v-if="errorMsg" class="error-message">
          {{ errorMsg }}
        </div>
      </form>

      <div class="divider"></div>

      <div class="links">
        <router-link to="/detect" class="link-face">人脸识别登录</router-link>
        <router-link to="/collect">还没有账号？点击去注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { passwordLogin } from '@/api'
import { useUserStore } from '@/stores'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginAccount = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function handleLogin() {
  if (loading.value) return

  errorMsg.value = ''
  loading.value = true

  try {
    const response = await passwordLogin(loginAccount.value, password.value)

    if (response.code === 200) {
      userStore.loginSuccess({
        user_id: response.data.user_id,
        user_name: response.data.user_name,
        user_age: response.data.user_age,
        user_phone: response.data.user_phone
      })
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      errorMsg.value = response.msg || '登录失败，请重试'
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMsg.value = '网络错误，请检查后端服务是否启动'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background: var(--color-background-secondary);
}

.login-container {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 40px;
  max-width: 420px;
  width: 100%;
  box-shadow: var(--shadow-md);
}

.brand {
  text-align: center;
  color: var(--color-primary);
  margin-bottom: 4px;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 1px;
}

.brand-desc {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  color: var(--color-text-primary);
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 14px;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: var(--transition);
  background: var(--color-background);
  color: var(--color-text-primary);
}

input[type="text"]:focus,
input[type="password"]:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

input::placeholder {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  margin-top: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  display: block;
  text-align: center;
  color: var(--color-error);
  margin-top: 16px;
  font-size: 14px;
  padding: 10px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-md);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.divider {
  height: 1px;
  background: var(--color-border);
  margin: 24px 0;
}

.links {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.links a {
  color: var(--color-text-secondary);
  font-size: 14px;
  transition: var(--transition);
  padding: 8px;
  border-radius: var(--radius-sm);
}

.link-face {
  color: var(--color-primary) !important;
  font-weight: 500;
}

.links a:hover {
  color: var(--color-primary);
  background: var(--color-background-secondary);
}

@media (max-width: 600px) {
  .login-container {
    padding: 32px 24px;
  }

  .brand {
    font-size: 24px;
  }
}
</style>
