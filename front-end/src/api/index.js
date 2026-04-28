const BASE_URL = import.meta.env.DEV ? '' : ''

async function request(url, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include'
  }

  const finalOptions = { ...defaultOptions, ...options }

  try {
    const response = await fetch(`${BASE_URL}${url}`, finalOptions)
    const text = await response.text()
    if (!text) {
      return { code: response.status, msg: '服务器无响应' }
    }
    try {
      const data = JSON.parse(text)
      if (data.code === 401) {
        localStorage.removeItem('zhiTu_logged_in')
        localStorage.removeItem('zhiTu_user_info')
        window.location.href = '/login'
      }
      return data
    } catch {
      return { code: response.status, msg: text || '服务器响应格式错误' }
    }
  } catch (error) {
    console.error('请求失败:', error)
    throw error
  }
}

export async function register(data) {
  return request('/api/v1/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function passwordLogin(login_account, user_pwd) {
  return request('/api/v1/auth/login/password/', {
    method: 'POST',
    body: JSON.stringify({ login_account, user_pwd })
  })
}

export async function faceLogin(face_image) {
  return request('/api/v1/auth/login/face/', {
    method: 'POST',
    body: JSON.stringify({ face_image })
  })
}

export async function logout() {
  return request('/api/v1/auth/logout/', {
    method: 'POST'
  })
}

export async function getUserProfile() {
  return request('/api/v1/user/profile/', {
    method: 'POST'
  })
}

export async function updateUserProfile(data) {
  return request('/api/v1/user/profile/', {
    method: 'POST',
    body: JSON.stringify({ ...data, action: 'update' })
  })
}

export async function getSessions() {
  return request('/api/v1/chat/sessions/', {
    method: 'GET'
  })
}

export async function createSession(title = '新会话') {
  return request('/api/v1/chat/sessions/', {
    method: 'POST',
    body: JSON.stringify({ title })
  })
}

export async function getSessionMessages(sessionId) {
  return request(`/api/v1/chat/sessions/${sessionId}/messages/`, {
    method: 'GET'
  })
}

export async function deleteSession(sessionId) {
  return request(`/api/v1/chat/sessions/${sessionId}/`, {
    method: 'DELETE'
  })
}

export async function chatAgent(sessionId, content, deepThinking = false) {
  const params = new URLSearchParams({
    session_id: String(sessionId),
    content: content,
    deep_thinking: String(deepThinking)
  })
  const url = `${BASE_URL}/api/v1/chat/agent/?${params.toString()}`
  const response = await fetch(url, { credentials: 'include' })
  return response
}

export async function getMcpJobs(keyword, city, limit = 20) {
  const params = new URLSearchParams()
  if (keyword) params.append('keyword', keyword)
  if (city) params.append('city', city)
  params.append('limit', String(limit))
  return request(`/api/v1/mcp/jobs/?${params.toString()}`, {
    method: 'GET'
  })
}

export default {
  register,
  passwordLogin,
  faceLogin,
  logout,
  getUserProfile,
  updateUserProfile,
  getSessions,
  createSession,
  getSessionMessages,
  deleteSession,
  chatAgent,
  getMcpJobs
}
