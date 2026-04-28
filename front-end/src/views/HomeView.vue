<template>
  <div class="home-page">
    <header class="top-bar">
      <div class="top-bar-left">
        <span class="logo">职途AI</span>
      </div>
      <div class="top-bar-right">
        <div
          class="deep-thinking-toggle"
          :class="{ active: chatStore.deepThinking }"
          @click="chatStore.toggleDeepThinking()"
          :title="chatStore.deepThinking ? '关闭深度思考' : '开启后展示大模型思考过程'"
        >
          <svg class="icon-brain" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.3 6l-.7.5V18a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2v-2.5l-.7-.5A7 7 0 0 1 12 2z"/>
            <path d="M10 22h4"/>
          </svg>
          <span class="toggle-label">{{ chatStore.deepThinking ? '深度思考：开启' : '深度思考：关闭' }}</span>
        </div>
        <div class="user-menu-wrapper" ref="menuRef">
          <div class="user-avatar" @click="showMenu = !showMenu">
            {{ userStore.userName?.charAt(0) || '?' }}
          </div>
          <div v-if="showMenu" class="user-dropdown">
            <div class="dropdown-item" @click="goProfile">个人中心</div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item dropdown-item-danger" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </header>

    <div class="chat-container">
      <aside class="sidebar">
        <div class="sidebar-header">
          <button class="new-chat-btn" @click="newChat">+ 新建会话</button>
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
            <div class="empty-state-icon">📭</div>
            <div>暂无历史会话</div>
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div class="chat-box" ref="chatBoxRef">
          <div
            v-for="msg in messages"
            :key="msg.message_id"
            class="message"
            :class="msg.role === 'user' ? 'message-user' : 'message-agent'"
          >
            <div class="message-content">
              <div class="message-name">{{ msg.role === 'user' ? '用户' : '职途AI' }}</div>

              <div v-if="msg.role === 'assistant' && msg.thinking_process" class="thinking-box" :class="{ collapsed: msg._thinkingCollapsed }">
                <div class="thinking-header" @click="msg._thinkingCollapsed = !msg._thinkingCollapsed">
                  <span class="thinking-icon">🔍</span>
                  <span class="thinking-title">
                    {{ msg._thinkingCollapsed ? '已完成思考（点击展开查看）' : '思考过程' }}
                  </span>
                  <span class="thinking-toggle">{{ msg._thinkingCollapsed ? '↓' : '↑' }}</span>
                  <button
                    v-if="!msg._thinkingCollapsed"
                    class="copy-thinking-btn"
                    @click.stop="copyThinking(msg)"
                    title="复制思考过程"
                  >复制</button>
                </div>
                <div v-if="!msg._thinkingCollapsed" class="thinking-body" v-html="formatThinking(msg.thinking_process)"></div>
              </div>

              <div v-if="msg.role === 'assistant' && msg._isThinking && !msg.thinking_process" class="thinking-indicator">
                <span class="thinking-icon">🔍</span> 思考中...
              </div>

              <div v-if="msg.content" class="message-text" v-html="renderMarkdown(msg.content)"></div>

              <div v-if="msg.role === 'assistant' && msg.echarts_config && msg.echarts_config.length" class="echarts-container">
                <div
                  v-for="(config, idx) in msg.echarts_config"
                  :key="idx"
                  class="echarts-chart"
                  :ref="el => setChartRef(el, msg.message_id, idx)"
                ></div>
              </div>
            </div>
          </div>

          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">🤖</div>
            <div class="welcome-title">您好！我是职途AI</div>
            <div class="welcome-desc">基于实时招聘数据，为您解析岗位技术栈需求，规划个性化学习路径</div>
            <div class="welcome-hint">示例：我是计算机专业，想投北京的Java实习生</div>
          </div>
        </div>

        <div class="input-container">
          <textarea
            ref="inputRef"
            v-model="userInput"
            @keydown.enter.exact.prevent="sendMsg"
            @keydown.enter.shift="() => {}"
            placeholder="输入你的查询... (Enter发送，Shift+Enter换行)"
            :disabled="isLoading"
            rows="1"
          ></textarea>
          <button class="btn-send" @click="sendMsg" :disabled="isLoading || !userInput.trim()">
            {{ isLoading ? '发送中...' : '发送' }}
          </button>
        </div>
        <div class="input-hint">示例：我是计算机专业，想投贵阳的Python后端实习生</div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getSessions, createSession, getSessionMessages, deleteSession as deleteSessionApi, chatAgent, logout } from '@/api'
import { useUserStore, useChatStore } from '@/stores'
import echarts from '@/utils/echarts'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()

const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const userInput = ref('')
const isLoading = ref(false)
const chatBoxRef = ref(null)
const inputRef = ref(null)
const showMenu = ref(false)
const menuRef = ref(null)

const chartInstances = new Map()
const chartRefsMap = new Map()

function setChartRef(el, messageId, idx) {
  if (!el) return
  const key = `${messageId}_${idx}`
  chartRefsMap.set(key, el)
}

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

function formatThinking(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  html = html.replace(/\[工具调用\](.*?)(\n|$)/g, '<span class="tk-tool-call">[工具调用]$1</span>$2')
  html = html.replace(/\[工具返回\](.*?)(\n|$)/g, '<span class="tk-tool-return">[工具返回]$1</span>$2')
  html = html.replace(/\[数据分析\](.*?)(\n|$)/g, '<span class="tk-data-analysis">[数据分析]$1</span>$2')
  html = html.replace(/\n/g, '<br>')
  return html
}


function renderMarkdownTable(tableText) {
  const lines = tableText.split('\n').filter(l => l.trim())
  if (lines.length < 2) return tableText
  const parseRow = (line) => line.split('|').map(c => c.trim()).filter(Boolean)
  const headerCells = parseRow(lines[0])
  const separatorLine = lines[1]
  if (!/^\s*\|[\s-|]+\|/.test(separatorLine)) return tableText
  const bodyLines = lines.slice(2)
  let h = '<table class="md-table"><thead><tr>'
  headerCells.forEach(c => { h += '<th>' + c + '</th>' })
  h += '</tr></thead><tbody>'
  bodyLines.forEach(line => {
    const cells = parseRow(line)
    if (cells.length === 0) return
    h += '<tr>'
    cells.forEach(c => { h += '<td>' + c + '</td>' })
    h += '</tr>'
  })
  h += '</tbody></table>'
  return h
}

function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // 代码块（先保存，避免干扰表格解析）
  const codeBlocks = []
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    codeBlocks.push('<pre class="code-block"><code>' + code + '</code></pre>')
    return '%%CODEBLOCK_' + (codeBlocks.length - 1) + '%%'
  })
  // 行内代码（先保存）
  const inlineCodes = []
  html = html.replace(/`([^`]+)`/g, (_, code) => {
    inlineCodes.push('<code class="inline-code">' + code + '</code>')
    return '%%INLINECODE_' + (inlineCodes.length - 1) + '%%'
  })
  // 处理段落（按空行分割），识别表格
  const paragraphs = html.split(/\n\n+/)
  html = paragraphs.map(p => {
    // 检测是否为 Markdown 表格（包含 | 分隔符且第二行是 --- 分隔线）
    const tableMatch = p.match(/^(\|[^\n|]+\|)\n(\|[\s-|]+\|)\n((?:\|[^\n]+\|\n?)+)/)
    if (tableMatch) {
      const fullTable = tableMatch[0]
      const tableHtml = renderMarkdownTable(fullTable)
      return p.replace(fullTable, tableHtml)
    }
    // 普通段落：先处理行内格式
    let result = p
    result = result.replace(/^### (.+)$/gm, '<h4>$1</h4>')
    result = result.replace(/^## (.+)$/gm, '<h3>$1</h3>')
    result = result.replace(/^# (.+)$/gm, '<h3>$1</h3>')
    result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    result = result.replace(/\*(.+?)\*/g, '<em>$1</em>')
    result = result.replace(/^\d+\.\s+(.+)$/gm, '<div class="list-item-num">$1</div>')
    result = result.replace(/^[-*]\s+(.+)$/gm, '<div class="list-item">• $1</div>')
    result = result.replace(/\n/g, '<br>')
    return '<p>' + result + '</p>'
  }).join('')
  // 恢复代码块
  html = html.replace(/%%CODEBLOCK_(\d+)%%/g, (_, i) => codeBlocks[parseInt(i)])
  html = html.replace(/%%INLINECODE_(\d+)%%/g, (_, i) => inlineCodes[parseInt(i)])
  return html
}

function copyThinking(msg) {
  if (msg.thinking_process) {
    navigator.clipboard.writeText(msg.thinking_process).then(() => {
      const btn = event.target
      const original = btn.textContent
      btn.textContent = '已复制'
      setTimeout(() => { btn.textContent = original }, 1500)
    }).catch(() => {})
  }
}

function renderChartsForMessage(msg) {
  if (!msg.echarts_config || !msg.echarts_config.length) return
  nextTick(() => {
    msg.echarts_config.forEach((config, idx) => {
      const key = `${msg.message_id}_${idx}`
      const el = chartRefsMap.get(key)
      if (!el) return

      const existing = chartInstances.get(key)
      if (existing) {
        existing.dispose()
      }

      const chart = echarts.init(el)
      chart.setOption(config)
      chartInstances.set(key, chart)
    })
  })
}

function handleResize() {
  chartInstances.forEach(chart => {
    if (chart && !chart.isDisposed()) {
      chart.resize()
    }
  })
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
      messages.value = response.data.messages.map(msg => ({
        ...msg,
        _thinkingCollapsed: !!msg.thinking_process,
        _isThinking: false
      }))
      scrollToBottom()
      nextTick(() => {
        messages.value.forEach(msg => {
          if (msg.role === 'assistant' && msg.echarts_config) {
            renderChartsForMessage(msg)
          }
        })
      })
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
    created_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
    _isThinking: false
  })
  scrollToBottom()

  isLoading.value = true

  const assistantMsg = {
    message_id: Date.now() + 1,
    role: 'assistant',
    content: '',
    thinking_process: null,
    echarts_config: null,
    created_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
    _thinkingCollapsed: false,
    _isThinking: chatStore.deepThinking
  }
  messages.value.push(assistantMsg)
  scrollToBottom()

  try {
    const response = await chatAgent(currentSessionId.value, content, chatStore.deepThinking)

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let hasError = false

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

          if (currentEvent === 'thinking') {
            if (!assistantMsg.thinking_process) assistantMsg.thinking_process = ''
            assistantMsg.thinking_process += data
            assistantMsg._isThinking = true
            scrollToBottom()
          } else if (currentEvent === 'thinking_end') {
            assistantMsg._isThinking = false
            assistantMsg._thinkingCollapsed = true
            scrollToBottom()
          } else if (currentEvent === 'content') {
            assistantMsg._isThinking = false
            assistantMsg.content += data
            scrollToBottom()
          } else if (currentEvent === 'echarts') {
            try {
              const echartsConfig = JSON.parse(data)
              if (!assistantMsg.echarts_config) assistantMsg.echarts_config = []
              assistantMsg.echarts_config.push(echartsConfig)
              nextTick(() => renderChartsForMessage(assistantMsg))
            } catch (e) {
              // ignore
            }
          } else if (currentEvent === 'error') {
            hasError = true
            assistantMsg._isThinking = false
            assistantMsg.content = data || '发生错误，请稍后重试'
            scrollToBottom()
          } else if (currentEvent === 'end') {
            assistantMsg._isThinking = false
          }

          currentEvent = null
        }
      }
    }

    if (!hasError) {
      assistantMsg._isThinking = false
    }

    await loadSessions()
  } catch (error) {
    console.error('发送消息失败:', error)
    assistantMsg._isThinking = false
    assistantMsg.content = '抱歉，发生了错误，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}

function goProfile() {
  showMenu.value = false
  router.push('/profile')
}

async function handleLogout() {
  showMenu.value = false
  try {
    await logout()
  } catch (e) {
    // ignore
  }
  userStore.logout()
  router.push('/login')
}

function handleClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    showMenu.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
  await loadSessions()
  if (sessions.value.length > 0) {
    await loadSession(sessions.value[0].session_id)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
  chartInstances.clear()
})
</script>

<style scoped>
.home-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-background);
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.top-bar-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 1px;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.deep-thinking-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  cursor: pointer;
  transition: var(--transition);
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 13px;
  user-select: none;
}

.deep-thinking-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.deep-thinking-toggle.active {
  background: rgba(37, 99, 235, 0.08);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.icon-brain {
  width: 16px;
  height: 16px;
}

.toggle-label {
  font-weight: 500;
}

.user-menu-wrapper {
  position: relative;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
}

.user-avatar:hover {
  background: var(--color-primary-hover);
}

.user-dropdown {
  position: absolute;
  top: 44px;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 140px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 16px;
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: var(--transition);
}

.dropdown-item:hover {
  background: var(--color-background-secondary);
}

.dropdown-item-danger {
  color: var(--color-error);
}

.dropdown-item-danger:hover {
  background: rgba(239, 68, 68, 0.08);
}

.dropdown-divider {
  height: 1px;
  background: var(--color-border);
}

.chat-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 260px;
  background: var(--color-background-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
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
  padding: 8px;
}

.history-item {
  padding: 10px 12px;
  margin-bottom: 4px;
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
  background: rgba(37, 99, 235, 0.04);
}

.history-title {
  font-size: 13px;
  color: var(--color-text-primary);
  margin-bottom: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 24px;
}

.history-time {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  border-radius: 50%;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.08);
}

.empty-state {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 40px 16px;
  font-size: 14px;
}

.empty-state-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  scroll-behavior: smooth;
}

.welcome-message {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 80px 20px;
}

.welcome-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.welcome-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.welcome-desc {
  font-size: 14px;
  margin-bottom: 20px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.welcome-hint {
  font-size: 13px;
  color: var(--color-primary);
  background: rgba(37, 99, 235, 0.06);
  display: inline-block;
  padding: 8px 16px;
  border-radius: var(--radius-md);
}

.message {
  margin-bottom: 20px;
}

.message-user {
  display: flex;
  justify-content: flex-end;
}

.message-agent {
  display: flex;
  justify-content: flex-start;
}

.message-content {
  max-width: 72%;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  word-wrap: break-word;
  line-height: 1.7;
}

.message-user .message-content {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-agent .message-content {
  background: var(--color-background-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 4px;
}

.message-name {
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 6px;
  opacity: 0.7;
}

.message-text {
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
  overflow-wrap: break-word;
}

.message-text :deep(p) {
  margin: 0;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
  font-size: 13px;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid var(--color-border);
  padding: 6px 12px;
  text-align: left;
}

.message-text :deep(th) {
  background: var(--color-background-secondary);
  font-weight: 600;
}

.message-text :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 12px 0 6px;
}

.message-text :deep(h4) {
  font-size: 15px;
  font-weight: 600;
  margin: 10px 0 4px;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(.code-block) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
  margin: 8px 0;
}

.message-text :deep(.inline-code) {
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-text :deep(.list-item),
.message-text :deep(.list-item-num) {
  padding-left: 8px;
  margin: 2px 0;
}

.thinking-box {
  margin-bottom: 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-background);
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--color-background-secondary);
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  user-select: none;
  transition: var(--transition);
}

.thinking-header:hover {
  background: var(--color-border);
}

.thinking-icon {
  font-size: 14px;
}

.thinking-title {
  flex: 1;
  font-weight: 500;
}

.thinking-toggle {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.copy-thinking-btn {
  padding: 2px 10px;
  font-size: 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.copy-thinking-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.thinking-body {
  padding: 12px 16px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.thinking-body :deep(.tk-tool-call) {
  color: #2563EB;
  font-weight: 500;
}

.thinking-body :deep(.tk-tool-return) {
  color: #10B981;
  font-weight: 500;
}

.thinking-body :deep(.tk-data-analysis) {
  color: #F59E0B;
  font-weight: 500;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  padding: 4px 0;
  margin-bottom: 8px;
}

.echarts-container {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.echarts-chart {
  width: 100%;
  height: 400px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  padding: 12px 24px 0;
  flex-shrink: 0;
}

textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: var(--transition);
  background: var(--color-background);
  color: var(--color-text-primary);
  resize: none;
  max-height: 120px;
  line-height: 1.5;
  font-family: inherit;
}

textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

textarea::placeholder {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.btn-send {
  padding: 12px 28px;
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-hint {
  padding: 6px 24px 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }

  .message-content {
    max-width: 88%;
  }

  .echarts-chart {
    height: 300px;
  }
}
</style>
