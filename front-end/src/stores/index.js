import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const isLoggedIn = ref(false)
  const userInfo = ref(null)

  function loginSuccess(user) {
    isLoggedIn.value = true
    userInfo.value = user
  }

  function logout() {
    isLoggedIn.value = false
    userInfo.value = null
  }

  return {
    isLoggedIn,
    userInfo,
    loginSuccess,
    logout
  }
})

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const historySessions = ref([])
  const currentSessionIndex = ref(-1)

  const currentSession = ref(null)

  function addMessage(message) {
    messages.value.push(message)
  }

  function updateLastMessage(text) {
    if (messages.value.length > 0) {
      messages.value[messages.value.length - 1].text = text
    }
  }

  function newChat() {
    messages.value = []
    currentSessionIndex.value = -1
  }

  function saveCurrentSession() {
    if (messages.value.length === 0) return

    const now = new Date()
    const timeStr = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })

    const firstUserMsg = messages.value.find(msg => msg.name === '用户')
    const title = firstUserMsg
      ? firstUserMsg.text.substring(0, 20) + (firstUserMsg.text.length > 20 ? '...' : '')
      : '新对话'

    const session = {
      title,
      time: timeStr,
      messages: JSON.parse(JSON.stringify(messages.value))
    }

    if (currentSessionIndex.value >= 0) {
      historySessions.value[currentSessionIndex.value] = session
    } else {
      historySessions.value.unshift(session)
      currentSessionIndex.value = 0
    }

    saveHistoryToStorage()
  }

  function loadSession(index) {
    if (index < 0 || index >= historySessions.value.length) return
    currentSessionIndex.value = index
    messages.value = JSON.parse(JSON.stringify(historySessions.value[index].messages))
  }

  function deleteSession(index) {
    historySessions.value.splice(index, 1)
    if (currentSessionIndex.value === index) {
      messages.value = []
      currentSessionIndex.value = -1
    } else if (currentSessionIndex.value > index) {
      currentSessionIndex.value--
    }
    saveHistoryToStorage()
  }

  function saveHistoryToStorage() {
    try {
      localStorage.setItem('chat_history', JSON.stringify(historySessions.value))
    } catch (e) {
      console.error('保存历史记录失败:', e)
    }
  }

  function loadHistoryFromStorage() {
    try {
      const stored = localStorage.getItem('chat_history')
      if (stored) {
        historySessions.value = JSON.parse(stored)
      }
    } catch (e) {
      console.error('加载历史记录失败:', e)
      historySessions.value = []
    }
  }

  return {
    messages,
    historySessions,
    currentSessionIndex,
    currentSession,
    addMessage,
    updateLastMessage,
    newChat,
    saveCurrentSession,
    loadSession,
    deleteSession,
    saveHistoryToStorage,
    loadHistoryFromStorage
  }
})
