/**
 * 摄像头工具函数
 * 用于人脸采集和识别的摄像头控制
 */

import { ref, onUnmounted } from 'vue'

/**
 * 摄像头控制 Hook
 * @param {object} options - 配置选项
 * @param {number} options.width - 视频宽度
 * @param {number} options.height - 视频高度
 * @returns {object} 摄像头控制方法和状态
 */
export function useCamera(options = {}) {
  const {
    width = 500,
    height = 600
  } = options

  // 响应式状态
  const isOpen = ref(false)
  const videoRef = ref(null)
  const canvasRef = ref(null)
  const stream = ref(null)
  const error = ref(null)

  /**
   * 打开摄像头
   * @param {HTMLVideoElement} videoElement - 视频元素
   * @param {HTMLCanvasElement} canvasElement - 画布元素
   */
  async function openCamera(videoElement, canvasElement) {
    if (!videoElement || !canvasElement) {
      error.value = '视频元素或画布元素未提供'
      return false
    }

    videoRef.value = videoElement
    canvasRef.value = canvasElement

    try {
      const constraints = {
        video: {
          width: { ideal: width },
          height: { ideal: height },
          facingMode: 'user'
        },
        audio: false
      }

      stream.value = await navigator.mediaDevices.getUserMedia(constraints)
      videoElement.srcObject = stream.value
      await videoElement.play()
      
      isOpen.value = true
      error.value = null
      return true
    } catch (err) {
      console.error('摄像头打开失败:', err)
      error.value = '无法访问摄像头，请确保已授权摄像头权限'
      isOpen.value = false
      return false
    }
  }

  /**
   * 关闭摄像头
   */
  function closeCamera() {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
    }
    
    if (videoRef.value) {
      videoRef.value.srcObject = null
    }
    
    isOpen.value = false
  }

  /**
   * 获取当前帧的 base64 编码图像
   * @returns {string|null} base64 编码的图像数据
   */
  function getFrameAsBase64() {
    if (!isOpen.value || !videoRef.value || !canvasRef.value) {
      return null
    }

    const ctx = canvasRef.value.getContext('2d')
    canvasRef.value.width = width
    canvasRef.value.height = height
    ctx.drawImage(videoRef.value, 0, 0, width, height)
    
    return canvasRef.value.toDataURL('image/png')
  }

  /**
   * 截取当前帧并返回 Blob 对象
   * @returns {Promise<Blob|null>} 图像 Blob 对象
   */
  function getFrameAsBlob() {
    return new Promise((resolve) => {
      if (!isOpen.value || !videoRef.value || !canvasRef.value) {
        resolve(null)
        return
      }

      const ctx = canvasRef.value.getContext('2d')
      canvasRef.value.width = width
      canvasRef.value.height = height
      ctx.drawImage(videoRef.value, 0, 0, width, height)
      
      canvasRef.value.toBlob((blob) => {
        resolve(blob)
      }, 'image/png')
    })
  }

  // 组件卸载时自动关闭摄像头
  onUnmounted(() => {
    closeCamera()
  })

  return {
    isOpen,
    error,
    openCamera,
    closeCamera,
    getFrameAsBase64,
    getFrameAsBlob
  }
}

/**
 * 人脸工具类（兼容旧版 API）
 */
export const faceUtil = {
  width: 500,
  height: 600,
  isOpen: false,
  stream: null,

  /**
   * 打开摄像头
   * @param {string} containerId - 容器元素 ID
   */
  async openVideo(containerId) {
    const container = document.getElementById(containerId)
    if (!container) return

    // 清空容器
    container.innerHTML = ''

    // 创建视频元素
    const video = document.createElement('video')
    video.id = 'myVideo'
    video.width = this.width
    video.height = this.height
    video.autoplay = true
    video.style.marginTop = '0px'
    video.style.borderRadius = '15px'
    video.style.width = '100%'
    video.style.height = 'auto'

    // 创建画布元素
    const canvas = document.createElement('canvas')
    canvas.id = 'myCanvas'
    canvas.width = this.width
    canvas.height = this.height
    canvas.style.display = 'none'

    container.appendChild(video)
    container.appendChild(canvas)

    try {
      const constraints = {
        video: { width: this.width, height: this.height },
        audio: false
      }

      this.stream = await navigator.mediaDevices.getUserMedia(constraints)
      video.srcObject = this.stream
      await video.play()
      this.isOpen = true
    } catch (err) {
      console.error('摄像头打开失败:', err)
      alert('无法访问摄像头，请确保已授权摄像头权限')
      this.isOpen = false
    }
  },

  /**
   * 关闭摄像头
   */
  closeVideo() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    this.isOpen = false
  },

  /**
   * 获取图像 base64 编码
   * @returns {string|null} base64 编码的图像数据
   */
  getDecode() {
    if (!this.isOpen) {
      alert('没有开启摄像头')
      return null
    }

    const video = document.getElementById('myVideo')
    const canvas = document.getElementById('myCanvas')
    
    if (!video || !canvas) {
      alert('视频元素未找到')
      return null
    }

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, this.width, this.height)
    
    return canvas.toDataURL('image/png')
  }
}

export default faceUtil
