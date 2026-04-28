<template>
  <div class="chat-page">
    <div class="chat-container">
      <div class="sidebar">
        <div class="sidebar-header">
          <h2>历史会话</h2>
          <button class="new-chat-btn" @click="newChat">+ 新建对话</button>
        </div>
        <div class="history-list">
          <div 
            v-for="session in sessions" 
            :key="session.session_id" 
            class="history-item"
            :class="{ active: currentSessionId === session.session_id }"
            @click="loadSession(session.session_id)"
          >
            <div class="history-title">{{ session.title }}</div>
            <div class="history-time">{{ formatTime(session.last_message_time) }}</div>
            <button 
              class="delete-btn" 
              @click.stop="handleDeleteSession(session.session_id)" 
              title="删除会话"
            >×</button>
          </div>
          <div v-if="sessions.length === 0" class="empty-state">
            <div class="empty-state-text">暂无历史会话</div>
          </div>
        </div>
      </div>
      
      <div class="main-content">
        <h1>智能体对话</h1>
        <div class="chat-box" ref="chatBoxRef">
          <div 
            v-for="msg in messages" 
            :key="msg.message_id" 
            class="message" 
            :class="msg.role === 'user' ? 'message-user' : 'message-agent'"
          >
            <div class="message-content">
              <div class="message-name">{{ msg.role === 'user' ? '用户' : '智能体' }}</div>
              <div class="message-text">{{ msg.content }}</div>
            </div>
          </div>
          <div v-if="messages.length === 0" class="welcome-message">
            <div>您好！我是 AI 智能助手，有什么可以帮您的吗？</div>
          </div>
        </div>
        <div class="input-container">
          <input
            type="text"
            v-model="userInput"
            @keyup.enter="sendMsg"
            placeholder="请输入您的问题"
            :disabled="isLoading"
          >
          <button @click="sendMsg" :disabled="isLoading || !userInput.trim()" class="btn-send">
            {{ isLoading ? '发送中...' : '发送信息' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getSessions, createSession, getSessionMessages, deleteSession as deleteSessionApi, chatAgent } from '@/api'

const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const userInput = ref('')
const isLoading = ref(false)
const chatBoxRef = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (chatBoxRef.value) {
      chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight
    }
  })
}

function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.replace('T', ' ')
}

async function loadSessions() {
  try {
    const response = await getSessions()
    if (response.code === 200) {
      sessions.value = response.data.sessions
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

async function loadSessionMessages(sessionId) {
  try {
    const response = await getSessionMessages(sessionId)
    if (response.code === 200) {
      messages.value = response.data.messages
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

async function loadSession(sessionId) {
  currentSessionId.value = sessionId
  await loadSessionMessages(sessionId)
}

async function newChat() {
  try {
    const response = await createSession()
    if (response.code === 200) {
      currentSessionId.value = response.data.session_id
      messages.value = []
      await loadSessions()
    }
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}

async function handleDeleteSession(sessionId) {
  if (!confirm('确定要删除这个会话吗？')) return
  try {
    const response = await deleteSessionApi(sessionId)
    if (response.code === 200) {
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
        messages.value = []
      }
      await loadSessions()
    }
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}

async function sendMsg() {
  if (!userInput.value.trim() || isLoading.value) return

  if (!currentSessionId.value) {
    await newChat()
    if (!currentSessionId.value) return
  }

  const content = userInput.value.trim()
  userInput.value = ''

  messages.value.push({
    message_id: Date.now(),
    role: 'user',
    content: content,
    thinking_process: null,
    echarts_config: null,
    created_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
  })
  scrollToBottom()

  isLoading.value = true

  const assistantMsg = {
    message_id: Date.now() + 1,
    role: 'assistant',
    content: '',
    thinking_process: null,
    echarts_config: null,
    created_at: new Date().toISOString().replace('T', ' ').slice(0, 19)
  }
  messages.value.push(assistantMsg)
  scrollToBottom()

  try {
    const response = await chatAgent(currentSessionId.value, content)

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = null
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ') && currentEvent) {
          const data = line.slice(6)

          if (currentEvent === 'content') {
            assistantMsg.content += data
            scrollToBottom()
          } else if (currentEvent === 'thinking') {
            if (!assistantMsg.thinking_process) assistantMsg.thinking_process = ''
            assistantMsg.thinking_process += data
          } else if (currentEvent === 'echarts') {
            try {
              assistantMsg.echarts_config = JSON.parse(data)
            } catch (e) {
              // ignore
            }
          } else if (currentEvent === 'error') {
            assistantMsg.content = data || '发生错误，请稍后重试'
            scrollToBottom()
          } else if (currentEvent === 'end') {
            // done
          }

          currentEvent = null
        }
      }
    }

    await loadSessions()
  } catch (error) {
    console.error('发送消息失败:', error)
    assistantMsg.content = '抱歉，发生了错误，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await loadSessions()
  if (sessions.value.length > 0) {
    await loadSession(sessions.value[0].session_id)
  }
})
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background: var(--color-background-secondary);
}

.chat-container {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  display: flex;
  max-width: 1200px;
  width: 100%;
  height: 85vh;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.sidebar {
  width: 280px;
  background: var(--color-background-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: var(--transition);
}

.sidebar-header {
  padding: 20px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h2 {
  font-size: 18px;
  margin-bottom: 12px;
  color: var(--color-text-primary);
  font-weight: 600;
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.new-chat-btn:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  padding: 12px;
  margin-bottom: 8px;
  background: var(--color-background);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid transparent;
  position: relative;
}

.history-item:hover {
  border-color: var(--color-border);
}

.history-item.active {
  border-color: var(--color-primary);
  background: rgba(37, 99, 235, 0.05);
}

.history-title {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transition: var(--transition);
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  opacity: 0.8;
}

.empty-state {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px 20px;
}

.empty-state-text {
  font-size: 14px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

h1 {
  text-align: center;
  color: var(--color-text-primary);
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 16px;
  background: var(--color-background-secondary);
  scroll-behavior: smooth;
}

.welcome-message {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px 20px;
  font-size: 14px;
}

.message {
  margin-bottom: 16px;
}

.message-user {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
}

.message-agent {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  word-wrap: break-word;
  line-height: 1.6;
}

.message-user .message-content {
  background: var(--color-primary);
  color: white;
}

.message-agent .message-content {
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.message-name {
  font-weight: 500;
  font-size: 12px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.message-text {
  font-size: 14px;
  white-space: pre-wrap;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

input[type="text"] {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: var(--transition);
  background: var(--color-background);
  color: var(--color-text-primary);
}

input[type="text"]:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

input::placeholder {
  color: var(--color-text-secondary);
}

.btn-send {
  padding: 12px 24px;
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
    height: 95vh;
  }

  .sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }

  .main-content {
    padding: 16px;
  }

  h1 {
    font-size: 20px;
  }

  .chat-box {
    height: 300px;
  }

  .message-content {
    max-width: 85%;
  }

  .btn-send {
    padding: 12px 16px;
  }
}
</style>
