import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(localStorage.getItem('zhiTu_logged_in') === 'true')
  const userInfo = ref(JSON.parse(localStorage.getItem('zhiTu_user_info') || 'null'))

  const userName = computed(() => userInfo.value?.user_name || '')

  function loginSuccess(user) {
    isLoggedIn.value = true
    userInfo.value = user
    localStorage.setItem('zhiTu_logged_in', 'true')
    localStorage.setItem('zhiTu_user_info', JSON.stringify(user))
  }

  function logout() {
    isLoggedIn.value = false
    userInfo.value = null
    localStorage.removeItem('zhiTu_logged_in')
    localStorage.removeItem('zhiTu_user_info')
  }

  function updateUserInfo(data) {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...data }
      localStorage.setItem('zhiTu_user_info', JSON.stringify(userInfo.value))
    }
  }

  return {
    isLoggedIn,
    userInfo,
    userName,
    loginSuccess,
    logout,
    updateUserInfo
  }
})

export const useChatStore = defineStore('chat', () => {
  const deepThinking = ref(localStorage.getItem('zhiTu_deep_thinking') === 'true')

  function toggleDeepThinking() {
    deepThinking.value = !deepThinking.value
    localStorage.setItem('zhiTu_deep_thinking', String(deepThinking.value))
  }

  function setDeepThinking(val) {
    deepThinking.value = val
    localStorage.setItem('zhiTu_deep_thinking', String(val))
  }

  return {
    deepThinking,
    toggleDeepThinking,
    setDeepThinking
  }
})
