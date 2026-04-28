<template>
  <div class="profile-page">
    <div class="nav-bar">
      <button class="back-btn" @click="$router.push('/')">
        返回首页
      </button>
      <h2>个人中心</h2>
      <button class="back-btn back-btn-danger" @click="handleLogout">退出</button>
    </div>

    <div v-if="errorMsg" class="error-banner">
      <span class="error-icon">⚠️</span>
      <span>{{ errorMsg }}</span>
      <button class="btn-retry-small" @click="loadUserInfo">重试</button>
    </div>

    <div class="profile-container" v-if="userInfo">
      <div class="avatar-section">
        <div class="avatar">{{ userInfo.user_name?.charAt(0) || '?' }}</div>
        <div class="user-name">{{ userInfo.user_name }}</div>
      </div>

      <div class="info-card">
        <div class="info-item">
          <div class="info-label">用户名</div>
          <div class="info-value">{{ userInfo.user_name }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">年龄</div>
          <div v-if="isEditing" class="info-edit">
            <input
              type="number"
              v-model.number="editData.user_age"
              min="0"
              max="150"
              placeholder="请输入年龄"
            >
          </div>
          <div v-else class="info-value">{{ userInfo.user_age || '未填写' }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">手机号</div>
          <div v-if="isEditing" class="info-edit">
            <input
              type="tel"
              v-model="editData.user_phone"
              placeholder="请输入手机号"
            >
          </div>
          <div v-else class="info-value">{{ userInfo.user_phone || '未填写' }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">注册时间</div>
          <div class="info-value">{{ formatDate(userInfo.created_at) }}</div>
        </div>

        <div v-if="isEditing" class="info-item">
          <div class="info-label">新密码</div>
          <div class="info-edit">
            <input
              type="password"
              v-model="editData.new_user_pwd"
              placeholder="留空则不修改密码"
            >
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button
          v-if="!isEditing"
          class="btn btn-edit"
          @click="startEdit"
        >
          编辑信息
        </button>
        <template v-else>
          <button class="btn btn-save" @click="saveInfo" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button class="btn btn-cancel" @click="cancelEdit">取消</button>
        </template>
      </div>
    </div>

    <div v-else class="loading-state">
      <p v-if="!errorMsg">加载用户信息中...</p>
      <div v-else class="error-state">
        <p class="error-text">{{ errorMsg }}</p>
        <button class="btn-retry" @click="loadUserInfo">重试</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { getUserProfile, updateUserProfile, logout } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const userInfo = ref(null)
const isEditing = ref(false)
const saving = ref(false)
const editData = ref({ user_age: null, user_phone: '', new_user_pwd: '' })
const errorMsg = ref('')

async function loadUserInfo() {
  errorMsg.value = ''
  try {
    const response = await getUserProfile()
    if (response.code === 200) {
      userInfo.value = response.data
      userStore.updateUserInfo({
        user_name: response.data.user_name,
        user_age: response.data.user_age,
        user_phone: response.data.user_phone
      })
    } else if (response.code === 401) {
      if (userStore.userInfo) {
        userInfo.value = userStore.userInfo
        errorMsg.value = '登录已过期，部分功能可能受限'
      } else {
        userStore.logout()
        router.push('/login')
      }
    } else {
      if (userStore.userInfo) {
        userInfo.value = userStore.userInfo
      }
      errorMsg.value = response.msg || '获取用户信息失败'
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    if (userStore.userInfo) {
      userInfo.value = userStore.userInfo
      errorMsg.value = '无法连接到服务器，显示本地缓存信息'
    } else {
      errorMsg.value = '无法连接到服务器，请检查后端服务是否启动'
    }
  }
}

function startEdit() {
  editData.value = {
    user_age: userInfo.value.user_age,
    user_phone: userInfo.value.user_phone || '',
    new_user_pwd: ''
  }
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
}

async function saveInfo() {
  if (saving.value) return

  if (editData.value.new_user_pwd && !/^(?=.*[a-zA-Z])(?=.*\d).{6,20}$/.test(editData.value.new_user_pwd)) {
    alert('密码需要6-20位，包含英文和数字')
    return
  }

  saving.value = true

  try {
    const data = {}
    if (editData.value.user_age !== null) data.user_age = editData.value.user_age
    if (editData.value.user_phone !== undefined) data.user_phone = editData.value.user_phone
    if (editData.value.new_user_pwd) data.new_user_pwd = editData.value.new_user_pwd

    const response = await updateUserProfile(data)
    if (response.code === 200) {
      isEditing.value = false
      await loadUserInfo()
    } else {
      alert(response.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存用户信息失败:', error)
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

async function handleLogout() {
  try {
    await logout()
  } catch (e) {
    // ignore
  }
  userStore.logout()
  router.push('/login')
}

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  try {
    return dateStr.replace('T', ' ')
  } catch {
    return dateStr
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--color-background-secondary);
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(239, 68, 68, 0.1);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--color-error);
  font-size: 14px;
}

.error-icon {
  font-size: 16px;
}

.btn-retry-small {
  padding: 4px 12px;
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: var(--transition);
  margin-left: 8px;
}

.btn-retry-small:hover {
  background: #DC2626;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-bar h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.back-btn {
  padding: 8px 16px;
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition);
  min-width: 72px;
}

.back-btn:hover {
  background: var(--color-border);
}

.back-btn-danger {
  color: var(--color-error);
}

.back-btn-danger:hover {
  background: rgba(239, 68, 68, 0.08);
  border-color: var(--color-error);
}

.profile-container {
  max-width: 560px;
  margin: 32px auto;
  padding: 0 20px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 32px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 32px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.info-card {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--color-text-secondary);
  font-size: 14px;
  min-width: 80px;
}

.info-value {
  color: var(--color-text-primary);
  font-size: 15px;
  font-weight: 500;
  text-align: right;
}

.info-edit input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-background);
  color: var(--color-text-primary);
  transition: var(--transition);
  text-align: right;
}

.info-edit input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.action-buttons {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.btn {
  flex: 1;
  padding: 14px;
  border: 1px solid;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-edit {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn-edit:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-save {
  background: var(--color-success);
  color: white;
  border-color: var(--color-success);
}

.btn-save:hover:not(:disabled) {
  background: #0EA472;
  border-color: #0EA472;
}

.btn-cancel {
  background: var(--color-background);
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-background-secondary);
}

.loading-state {
  text-align: center;
  padding: 100px 20px;
  color: var(--color-text-secondary);
  font-size: 15px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-text {
  color: var(--color-error);
  font-size: 14px;
  margin: 0;
}

.btn-retry {
  padding: 10px 24px;
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition);
}

.btn-retry:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

@media (max-width: 600px) {
  .profile-container {
    margin: 20px auto;
  }

  .info-item {
    padding: 14px 16px;
  }

  .user-name {
    font-size: 18px;
  }
}
</style>
