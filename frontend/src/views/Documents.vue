<template>
  <div class="documents-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工文档管理</span>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传文档
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索文档名称"
          style="width: 300px"
          clearable
          @keyup.enter="loadDocuments"
        />
        <el-select v-model="filterStatus" placeholder="审查状态" clearable style="width: 150px">
          <el-option label="待审查" value="pending" />
          <el-option label="审查中" value="reviewing" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-button type="primary" @click="loadDocuments">搜索</el-button>
      </div>

      <!-- 文档列表 -->
      <el-table :data="documents" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="name" label="文档名称" min-width="200" />
        <el-table-column prop="author" label="撰写人" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="status" label="审查状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看</el-button>
            <el-button link type="primary" @click="startReview(row)">开始审查</el-button>
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
        @size-change="loadDocuments"
        @current-change="loadDocuments"
      />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传员工文档" width="500px">
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
        <el-form-item label="文档名称" required>
          <el-input v-model="uploadForm.name" />
        </el-form-item>
        <el-form-item label="文档类型">
          <el-select v-model="uploadForm.type" placeholder="请选择">
            <el-option label="报告" value="报告" />
            <el-option label="方案" value="方案" />
            <el-option label="申请" value="申请" />
          </el-select>
        </el-form-item>
        <el-form-item label="撰写人">
          <el-input v-model="uploadForm.author" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="uploadForm.department" />
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload :auto-upload="false" :on-change="handleFileChange" :limit="1">
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
import { Upload } from '@element-plus/icons-vue'
import { getDocuments, uploadDocument, deleteDocument, type Document } from '@/api/documents'
import { getSystemStatus, type SystemStatus } from '@/api/system'

const loading = ref(false)
const documents = ref<Document[]>([])
const searchText = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  name: '',
  type: '',
  author: '',
  department: '',
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

const loadDocuments = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value
    const data = await getDocuments(params)
    if (data && 'items' in data) {
      documents.value = data.items || []
      total.value = data.total || 0
    } else {
      // 兼容旧格式
      documents.value = Array.isArray(data) ? data : []
      total.value = documents.value.length
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const handleUpload = async () => {
  if (!uploadForm.value.name || !selectedFile.value) {
    ElMessage.warning('请填写完整信息')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', uploadForm.value.name)
    if (uploadForm.value.type) formData.append('type', uploadForm.value.type)
    if (uploadForm.value.author) formData.append('author', uploadForm.value.author)
    if (uploadForm.value.department) formData.append('department', uploadForm.value.department)
    await uploadDocument(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    uploadForm.value = { name: '', type: '', author: '', department: '' }
    selectedFile.value = null
    // 重置到第一页并刷新列表
    currentPage.value = 1
    loadDocuments()
  } catch (error: any) {
    const errorMsg = error?.response?.data?.detail || error?.message || '上传失败'
    ElMessage.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    reviewing: 'warning',
    completed: 'success',
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审查',
    reviewing: '审查中',
    completed: '已完成',
  }
  return map[status] || status
}

const viewDetail = (row: Document) => {
  ElMessage.info('查看详情功能开发中')
}

const startReview = (row: Document) => {
  // 跳转到审查页面
  ElMessage.info('开始审查功能开发中')
}

const handleDelete = async (row: Document) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', { type: 'warning' })
    await deleteDocument(row.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.documents-page {
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

