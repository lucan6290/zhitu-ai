<template>
  <div class="detect-page">
    <div class="video-container" ref="videoContainerRef">
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

    <div class="action-container">
      <div class="brand">职途AI</div>
      <p class="brand-desc">人脸识别登录</p>
      <button
        type="button"
        @click="handleDetect"
        :disabled="loading"
        class="btn-primary"
      >
        {{ loading ? '识别中...' : '匹配人脸登录' }}
      </button>

      <div v-if="errorMsg" class="error-message">
        {{ errorMsg }}
      </div>

      <div class="divider"></div>

      <div class="links">
        <router-link to="/collect">还未注册？点击去注册</router-link>
        <router-link to="/login">账号密码登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { faceLogin } from '@/api'
import { useUserStore } from '@/stores'

const router = useRouter()
const userStore = useUserStore()

const videoRef = ref(null)
const canvasRef = ref(null)
const videoContainerRef = ref(null)
const cameraReady = ref(false)

const loading = ref(false)
const errorMsg = ref('')

let mediaStream = null

async function openCamera() {
  try {
    const constraints = {
      video: {
        width: { ideal: 500 },
        height: { ideal: 600 },
        facingMode: 'user'
      },
      audio: false
    }

    const stream = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      mediaStream = stream
      await videoRef.value.play()
      cameraReady.value = true
    }
  } catch (err) {
    console.error('[Camera] 摄像头打开失败:', err.name, err.message)
    errorMsg.value = `无法访问摄像头：${err.message}`
  }
}

function closeCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
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

async function handleDetect() {
  if (loading.value) return

  errorMsg.value = ''

  const face_image = getFrameAsBase64()
  if (!face_image) {
    errorMsg.value = '请先等待摄像头启动'
    return
  }

  loading.value = true

  try {
    const response = await faceLogin(face_image)

    if (response.code === 200) {
      userStore.loginSuccess({
        user_id: response.data.user_id,
        user_name: response.data.user_name,
        user_age: response.data.user_age,
        user_phone: response.data.user_phone
      })
      router.push('/')
    } else {
      errorMsg.value = response.msg || '识别失败'
    }
  } catch (error) {
    console.error('识别失败:', error)
    errorMsg.value = '请求失败，请检查后端服务'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  openCamera()
})

onUnmounted(() => {
  closeCamera()
})
</script>

<style scoped>
.detect-page {
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

.action-container {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 32px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: var(--shadow-md);
}

.brand {
  color: var(--color-primary);
  margin-bottom: 4px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
}

.brand-desc {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
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
  margin: 20px 0;
}

.links {
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
  .action-container {
    padding: 24px;
  }

  .brand {
    font-size: 22px;
  }
}
</style>
