<template>
  <div class="regulations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>制度文件管理</span>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传制度文件
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索制度名称或编号"
          style="width: 300px"
          clearable
          @clear="loadRegulations"
          @keyup.enter="loadRegulations"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterType"
          placeholder="制度类型"
          clearable
          style="width: 200px"
          @change="loadRegulations"
        >
          <el-option label="财务制度" value="财务制度" />
          <el-option label="人事制度" value="人事制度" />
          <el-option label="安全制度" value="安全制度" />
        </el-select>
        <el-button type="primary" @click="loadRegulations">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>

      <!-- 制度文件列表 -->
      <el-table :data="regulations" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="name" label="制度名称" min-width="200" />
        <el-table-column prop="code" label="制度编号" width="150" />
        <el-table-column prop="type" label="制度类型" width="120" />
        <el-table-column prop="uploader" label="上传人" width="120" />
        <el-table-column prop="upload_time" label="上传时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看</el-button>
            <el-button link type="primary" @click="editRegulation(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="loadRegulations"
        @current-change="loadRegulations"
      />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传制度文件" width="500px">
      <!-- 模型状态显示 -->
      <el-alert
        v-if="modelStatus"
        :type="modelStatus.llm_model ? 'success' : 'warning'"
        :title="modelStatus.llm_model ? 'AI模型就绪' : 'AI模型未就绪'"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <div class="model-status-info">
            <div class="status-item">
              <span class="label">Ollama服务:</span>
              <el-tag :type="modelStatus.ollama_service ? 'success' : 'danger'" size="small">
                {{ modelStatus.ollama_service ? '运行中' : '未运行' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">LLM模型:</span>
              <el-tag :type="modelStatus.llm_model ? 'success' : 'warning'" size="small">
                {{ modelStatus.llm_model ? modelStatus.llm_model_name : '未找到' }}
              </el-tag>
            </div>
            <div class="status-item" v-if="modelStatus.embedding_model">
              <span class="label">嵌入模型:</span>
              <el-tag type="success" size="small">{{ modelStatus.embedding_model_name }}</el-tag>
            </div>
            <div class="status-message" v-if="modelStatus.message">
              <el-text type="info" size="small">{{ modelStatus.message }}</el-text>
            </div>
          </div>
        </template>
      </el-alert>

      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="制度名称" required>
          <el-input v-model="uploadForm.name" />
        </el-form-item>
        <el-form-item label="制度编号">
          <el-input v-model="uploadForm.code" />
        </el-form-item>
        <el-form-item label="制度类型">
          <el-select v-model="uploadForm.type" placeholder="请选择">
            <el-option label="财务制度" value="财务制度" />
            <el-option label="人事制度" value="人事制度" />
            <el-option label="安全制度" value="安全制度" />
          </el-select>
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="uploadForm.effective_date" type="date" />
        </el-form-item>
        <el-form-item label="上传人">
          <el-input v-model="uploadForm.uploader" />
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word、TXT、Markdown 格式</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search } from '@element-plus/icons-vue'
import { getRegulations, uploadRegulation, deleteRegulation, type Regulation } from '@/api/regulations'
import { getSystemStatus, type SystemStatus } from '@/api/system'

const loading = ref(false)
const regulations = ref<Regulation[]>([])
const searchText = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  name: '',
  code: '',
  type: '',
  effective_date: '',
  uploader: '',
})
const selectedFile = ref<File | null>(null)

// 模型状态
const modelStatus = ref<SystemStatus | null>(null)

// 加载模型状态
const loadModelStatus = async () => {
  try {
    const status = await getSystemStatus()
    modelStatus.value = status
  } catch (error) {
    console.error('获取模型状态失败:', error)
    // 如果获取失败，设置为默认状态
    modelStatus.value = {
      ollama_service: false,
      llm_model: false,
      embedding_model: false,
      llm_model_name: 'deepseek-r1:7b',
      embedding_model_name: 'nomic-embed-text',
      ollama_url: 'http://localhost:11434',
      message: '无法获取模型状态'
    }
  }
}

// 监听上传对话框打开，自动检查模型状态
watch(showUploadDialog, (newVal) => {
  if (newVal) {
    loadModelStatus()
  }
})

// 加载制度文件列表
const loadRegulations = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (searchText.value) {
      params.search = searchText.value
    }
    if (filterType.value) {
      params.type = filterType.value
    }
    const data = await getRegulations(params)
    if (data && 'items' in data) {
      regulations.value = data.items || []
      total.value = data.total || 0
    } else {
      // 兼容旧格式
      regulations.value = Array.isArray(data) ? data : []
      total.value = regulations.value.length
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

// 上传文件
const handleUpload = async () => {
  if (!uploadForm.value.name) {
    ElMessage.warning('请输入制度名称')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', uploadForm.value.name)
    if (uploadForm.value.code) formData.append('code', uploadForm.value.code)
    if (uploadForm.value.type) formData.append('type', uploadForm.value.type)
    // 处理日期格式
    if (uploadForm.value.effective_date) {
      const date = uploadForm.value.effective_date
      // 如果是Date对象，转换为ISO字符串
      if (date instanceof Date) {
        formData.append('effective_date', date.toISOString().split('T')[0])
      } else if (typeof date === 'string') {
        formData.append('effective_date', date)
      }
    }
    if (uploadForm.value.uploader) formData.append('uploader', uploadForm.value.uploader)

    await uploadRegulation(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    // 重置表单
    uploadForm.value = {
      name: '',
      code: '',
      type: '',
      effective_date: '',
      uploader: '',
    }
    selectedFile.value = null
    // 重置到第一页并刷新列表
    currentPage.value = 1
    loadRegulations()
  } catch (error: any) {
    const errorMsg = error?.response?.data?.detail || error?.message || '上传失败'
    ElMessage.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

// 查看详情
const viewDetail = (row: Regulation) => {
  ElMessage.info('查看详情功能开发中')
}

// 编辑
const editRegulation = (row: Regulation) => {
  ElMessage.info('编辑功能开发中')
}

// 删除
const handleDelete = async (row: Regulation) => {
  try {
    await ElMessageBox.confirm('确定要删除这个制度文件吗？', '提示', {
      type: 'warning',
    })
    await deleteRegulation(row.id)
    ElMessage.success('删除成功')
    loadRegulations()
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  loadRegulations()
})
</script>

<style scoped>
.regulations-page {
  max-width: 1600px;
  margin: 0 auto;
}

:deep(.el-card) {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: none;
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-bottom: 1px solid #ebeef5;
  padding: 16px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding: 16px 0;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table tr:hover) {
  background-color: #f5f7fa;
}

:deep(.el-button--link) {
  padding: 4px 8px;
  font-weight: 500;
}

.model-status-info {
  margin-top: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-item .label {
  font-size: 13px;
  color: #606266;
  min-width: 90px;
  font-weight: 500;
}

.status-message {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 16px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-pagination) {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

