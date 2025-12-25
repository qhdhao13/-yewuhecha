<template>
  <div class="document-preview">
    <el-dialog
      v-model="visible"
      :title="title"
      width="90%"
      :close-on-click-modal="false"
      @close="handleClose"
    >
      <div v-loading="loading" class="preview-content">
        <!-- PDF预览 -->
        <iframe
          v-if="fileType === 'pdf' && previewUrl"
          :src="previewUrl"
          class="preview-iframe"
          frameborder="0"
        />

        <!-- 文本文件预览 -->
        <div v-else-if="isTextFile && textContent" class="text-preview">
          <pre class="text-content">{{ textContent }}</pre>
        </div>

        <!-- Word文件提示 -->
        <div v-else-if="fileType === 'word'" class="word-preview">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <div class="word-preview-info">
                <p>Word文档暂不支持在线预览，请下载后查看。</p>
                <el-button type="primary" @click="handleDownload">下载文件</el-button>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 不支持的文件类型 -->
        <div v-else class="unsupported-preview">
          <el-alert
            type="warning"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>该文件类型暂不支持在线预览，请下载后查看。</p>
              <el-button type="primary" @click="handleDownload">下载文件</el-button>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleDownload">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  modelValue: boolean
  fileUrl?: string
  fileName?: string
  fileType?: string
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  fileUrl: '',
  fileName: '',
  fileType: '',
  title: '文档预览',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const loading = ref(false)
const textContent = ref('')

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const previewUrl = computed(() => {
  if (!props.fileUrl) return ''
  // 如果是相对路径，需要转换为完整URL
  if (props.fileUrl.startsWith('/')) {
    return `${window.location.origin}${props.fileUrl}`
  }
  return props.fileUrl
})

const isTextFile = computed(() => {
  const textTypes = ['txt', 'md', 'markdown', 'text']
  return textTypes.includes(props.fileType?.toLowerCase() || '')
})

// 加载文本内容
const loadTextContent = async () => {
  if (!props.fileUrl || !isTextFile.value) return

  loading.value = true
  try {
    const url = previewUrl.value
    const response = await fetch(url)
    if (response.ok) {
      textContent.value = await response.text()
    } else {
      ElMessage.error('加载文件内容失败')
    }
  } catch (error) {
    console.error('加载文本内容失败:', error)
    ElMessage.error('加载文件内容失败')
  } finally {
    loading.value = false
  }
}

// 下载文件
const handleDownload = () => {
  if (!props.fileUrl) {
    ElMessage.warning('文件链接不存在')
    return
  }
  const url = previewUrl.value
  const link = document.createElement('a')
  link.href = url
  link.download = props.fileName || 'download'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleClose = () => {
  visible.value = false
  textContent.value = ''
}

// 监听文件URL变化，加载文本内容
watch(
  () => [props.fileUrl, props.fileType, visible.value],
  ([url, type, isVisible]) => {
    if (isVisible && isTextFile.value && url) {
      loadTextContent()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.document-preview {
  /* 组件样式 */
}

.preview-content {
  min-height: 500px;
  max-height: 80vh;
  overflow: auto;
}

.preview-iframe {
  width: 100%;
  height: 80vh;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.text-preview {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.text-content {
  margin: 0;
  padding: 16px;
  background-color: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  color: #303133;
  max-height: 70vh;
  overflow: auto;
}

.word-preview,
.unsupported-preview {
  padding: 40px 20px;
  text-align: center;
}

.word-preview-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.word-preview-info p {
  margin: 0;
  color: #606266;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}
</style>
