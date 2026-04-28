<template>
  <div class="collect-page">
    <div v-if="useFace" class="video-container" ref="videoContainerRef">
      <video
        ref="videoRef"
        autoplay
        muted
        playsinline
        width="100%"
        height="100%"
        class="video-element"
      ></video>
      <canvas ref="canvasRef" style="display: none;"></canvas>
      <div v-if="!cameraReady" class="video-placeholder">
        <span>正在启动摄像头...</span>
      </div>
    </div>

    <div class="form-container">
      <h2>新用户注册</h2>

      <div class="form-group">
        <label>用户名</label>
        <input
          type="text"
          v-model="formData.user_name"
          placeholder="6-20字符，全局唯一"
        >
      </div>

      <div class="form-group">
        <label>密码</label>
        <input
          type="password"
          v-model="formData.user_pwd"
          placeholder="6-20位，英文加数字"
        >
      </div>

      <div class="form-group">
        <label>邀请码</label>
        <input
          type="text"
          v-model="formData.invitation_code"
          placeholder="请输入邀请码"
        >
      </div>

      <div class="form-group">
        <label class="switch-label">
          <span>录入人脸</span>
          <label class="switch">
            <input type="checkbox" v-model="useFace" @change="toggleCamera">
            <span class="slider"></span>
          </label>
        </label>
      </div>

      <button
        type="button"
        @click="handleCollect"
        :disabled="loading"
        class="btn-primary"
      >
        {{ loading ? '注册中...' : (useFace ? '采集人脸注册' : '账号密码注册') }}
      </button>

      <div class="divider"></div>

      <div class="links">
        <router-link to="/detect">已采集人脸，点击去登录</router-link>
        <router-link to="/login">已有账号？点击去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api'

const router = useRouter()

const videoRef = ref(null)
const canvasRef = ref(null)
const videoContainerRef = ref(null)
const cameraReady = ref(false)

const useFace = ref(false)

const formData = reactive({
  user_name: '',
  user_pwd: '',
  invitation_code: ''
})

const loading = ref(false)

let mediaStream = null

async function openCamera() {
  try {
    console.log('[Camera] 开始请求摄像头...')

    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(d => d.kind === 'videoinput')
    console.log('[Camera] 可用摄像头设备:', videoDevices.map(d => ({ label: d.label, deviceId: d.deviceId })))

    const constraints = {
      video: {
        width: { ideal: 500 },
        height: { ideal: 600 },
        facingMode: 'user'
      },
      audio: false
    }

    const realCamera = videoDevices.find(d => {
      const label = d.label.toLowerCase()
      return !label.includes('todesk') &&
             !label.includes('virtual') &&
             !label.includes('obs') &&
             !label.includes('manycam') &&
             !label.includes('snap') &&
             !label.includes('many')
    })

    if (realCamera) {
      constraints.video = {
        ...constraints.video,
        deviceId: { exact: realCamera.deviceId }
      }
      console.log('[Camera] 使用真实摄像头:', realCamera.label)
    } else {
      console.warn('[Camera] 未检测到真实摄像头，使用默认设备')
    }

    const stream = await navigator.mediaDevices.getUserMedia(constraints)
    console.log('[Camera] 摄像头权限已获取，轨道数:', stream.getTracks().length)

    const track = stream.getTracks()[0]
    console.log('[Camera] 轨道状态:', {
      enabled: track.enabled,
      muted: track.muted,
      readyState: track.readyState,
      label: track.label,
      settings: track.getSettings()
    })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      mediaStream = stream

      await new Promise((resolve, reject) => {
        const video = videoRef.value
        video.onloadedmetadata = () => {
          console.log('[Camera] 元数据已加载')
        }
        video.onplaying = () => {
          console.log('[Camera] 视频开始播放')
          resolve()
        }
        video.onerror = reject
        setTimeout(() => reject(new Error('视频播放超时')), 5000)
        video.play().catch(reject)
      })

      cameraReady.value = true
      console.log('[Camera] 摄像头已就绪，视频尺寸:', videoRef.value.videoWidth, 'x', videoRef.value.videoHeight)
    } else {
      console.error('[Camera] videoRef 为 null，无法绑定流')
    }
  } catch (err) {
    console.error('[Camera] 摄像头打开失败:', err.name, err.message)
    alert(`无法访问摄像头：${err.message}`)
  }
}

function closeCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  cameraReady.value = false
}

async function toggleCamera() {
  if (useFace.value) {
    await openCamera()
  } else {
    closeCamera()
  }
}

function getFrameAsBase64() {
  if (!videoRef.value || !canvasRef.value || !cameraReady.value) {
    return null
  }

  const ctx = canvasRef.value.getContext('2d')
  canvasRef.value.width = 500
  canvasRef.value.height = 600
  ctx.drawImage(videoRef.value, 0, 0, 500, 600)

  return canvasRef.value.toDataURL('image/png')
}

async function handleCollect() {
  if (loading.value) return

  if (!formData.user_name.trim()) {
    alert('请输入用户名')
    return
  }
  if (!/^(?=.*[a-zA-Z])(?=.*\d).{6,20}$/.test(formData.user_pwd)) {
    alert('密码需要6-20位，包含英文和数字')
    return
  }
  if (!formData.invitation_code.trim()) {
    alert('请输入邀请码')
    return
  }

  const payload = {
    user_name: formData.user_name,
    user_pwd: formData.user_pwd,
    invitation_code: formData.invitation_code
  }

  if (useFace.value) {
    const face_image = getFrameAsBase64()
    if (!face_image) {
      alert('请先开启摄像头')
      return
    }
    payload.face_image = face_image
  }

  loading.value = true

  try {
    const response = await register(payload)

    if (response.code === 200) {
      alert('注册成功！')
      router.push('/login')
    } else {
      alert(response.msg || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    alert('请求失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (useFace.value) {
    openCamera()
  }
})

onUnmounted(() => {
  closeCamera()
})
</script>

<style scoped>
.collect-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  flex-direction: column;
  gap: 24px;
  background: var(--color-background-secondary);
}

.video-container {
  width: 100%;
  max-width: 400px;
  height: 480px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: #000;
  position: relative;
  box-shadow: var(--shadow-md);
}

.video-element {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  display: block !important;
  background: #1a1a1a;
}

.video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  background: var(--color-background);
}

.form-container {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 40px;
  max-width: 480px;
  width: 100%;
  box-shadow: var(--shadow-md);
}

h2 {
  text-align: center;
  color: var(--color-text-primary);
  margin-bottom: 32px;
  font-size: 24px;
  font-weight: 600;
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

.switch-label {
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  margin-bottom: 0;
}

.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-border);
  transition: var(--transition);
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: '';
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: var(--transition);
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--color-primary);
}

input:checked + .slider:before {
  transform: translateX(22px);
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

.links a:hover {
  color: var(--color-primary);
  background: var(--color-background-secondary);
}

@media (max-width: 600px) {
  .form-container {
    padding: 32px 24px;
  }

  h2 {
    font-size: 22px;
  }
}
</style>
