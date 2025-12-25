<template>
  <div class="annotations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>标注管理</span>
          <div class="header-actions">
            <el-button type="success" @click="handleExportAll" :disabled="annotations.length === 0">
              <el-icon><Download /></el-icon>
              导出全部
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-bar">
        <el-select v-model="filterSeverity" placeholder="严重程度" clearable style="width: 150px">
          <el-option label="严重" value="critical" />
          <el-option label="一般" value="general" />
          <el-option label="轻微" value="minor" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="标注状态" clearable style="width: 150px">
          <el-option label="待确认" value="pending" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已忽略" value="ignored" />
        </el-select>
        <el-button type="primary" @click="loadAnnotations">搜索</el-button>
      </div>

      <!-- 标注列表 -->
      <el-table :data="annotations" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="issue_type" label="问题类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getIssueTypeText(row.issue_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">{{ getSeverityText(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="不符合内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="regulation_clause" label="对应制度条款" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看</el-button>
            <el-button link type="primary" @click="editAnnotation(row)">编辑</el-button>
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
        @size-change="loadAnnotations"
        @current-change="loadAnnotations"
      />
    </el-card>

    <!-- 标注详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="标注详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentAnnotation" class="annotation-detail">
        <!-- 基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="标注ID">{{ currentAnnotation.id }}</el-descriptions-item>
          <el-descriptions-item label="审查记录ID">{{ currentAnnotation.review_id }}</el-descriptions-item>
          <el-descriptions-item label="问题类型">
            <el-tag>{{ getIssueTypeText(currentAnnotation.issue_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityType(currentAnnotation.severity)">
              {{ getSeverityText(currentAnnotation.severity) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标注状态">
            <el-tag :type="getStatusType(currentAnnotation.status)">
              {{ getStatusText(currentAnnotation.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ new Date(currentAnnotation.create_time).toLocaleString('zh-CN') }}
          </el-descriptions-item>
          <el-descriptions-item label="位置信息" :span="2">
            {{ currentAnnotation.position || '未指定' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 不符合内容 -->
        <div class="detail-section">
          <h4>不符合内容</h4>
          <el-card shadow="never" class="content-card">
            <div class="content-text highlight-content">
              <span class="highlight-text">{{ currentAnnotation.content || '无' }}</span>
            </div>
            <div v-if="currentAnnotation.position" class="position-info">
              <el-icon><Location /></el-icon>
              <span>位置：{{ currentAnnotation.position }}</span>
            </div>
          </el-card>
        </div>

        <!-- 对应制度条款 -->
        <div class="detail-section">
          <h4>对应制度条款</h4>
          <el-card shadow="never" class="content-card">
            <div class="content-text">{{ currentAnnotation.regulation_clause || '无' }}</div>
          </el-card>
        </div>

        <!-- 不符合原因 -->
        <div class="detail-section">
          <h4>不符合原因</h4>
          <el-card shadow="never" class="content-card">
            <div class="content-text">{{ currentAnnotation.reason || '无' }}</div>
          </el-card>
        </div>

        <!-- 修改建议 -->
        <div class="detail-section">
          <h4>修改建议</h4>
          <el-card shadow="never" class="content-card">
            <div class="content-text">{{ currentAnnotation.suggestion || '无' }}</div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="success" @click="handleExportCurrent">导出</el-button>
        <el-button type="primary" @click="handleEditFromDetail">编辑</el-button>
      </template>
    </el-dialog>

    <!-- 标注编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑标注"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        v-if="editForm"
        :model="editForm"
        label-width="100px"
        :rules="editRules"
        ref="editFormRef"
      >
        <el-form-item label="标注状态" prop="status">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="editForm.severity" style="width: 100%">
            <el-option label="严重" value="critical" />
            <el-option label="一般" value="general" />
            <el-option label="轻微" value="minor" />
          </el-select>
        </el-form-item>
        <el-form-item label="不符合原因" prop="reason">
          <el-input
            v-model="editForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入不符合原因的详细说明"
          />
        </el-form-item>
        <el-form-item label="修改建议" prop="suggestion">
          <el-input
            v-model="editForm.suggestion"
            type="textarea"
            :rows="4"
            placeholder="请输入具体的修改建议"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location, Download } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getAnnotations,
  getAnnotation,
  updateAnnotation,
  deleteAnnotation,
  type Annotation,
  type AnnotationUpdateParams,
} from '@/api/annotations'
import { exportAnnotationsToJSON, exportAnnotationsToCSV } from '@/utils/export'

const loading = ref(false)
const annotations = ref<Annotation[]>([])
const filterSeverity = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 详情对话框
const showDetailDialog = ref(false)
const currentAnnotation = ref<Annotation | null>(null)

// 编辑对话框
const showEditDialog = ref(false)
const editFormRef = ref<FormInstance>()
const saving = ref(false)
const editForm = ref<AnnotationUpdateParams>({
  status: 'pending',
  severity: 'general',
  reason: '',
  suggestion: '',
})

// 编辑表单验证规则
const editRules: FormRules = {
  status: [{ required: true, message: '请选择标注状态', trigger: 'change' }],
  severity: [{ required: true, message: '请选择严重程度', trigger: 'change' }],
}

const loadAnnotations = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (filterSeverity.value) params.severity = filterSeverity.value
    if (filterStatus.value) params.status = filterStatus.value
    const data = await getAnnotations(params)
    annotations.value = Array.isArray(data) ? data : []
    total.value = annotations.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const getIssueTypeText = (type: string) => {
  const map: Record<string, string> = {
    content_mismatch: '内容不符',
    missing: '缺失',
    extra: '多余',
    format: '格式不符',
  }
  return map[type] || type
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    general: 'warning',
    minor: 'info',
  }
  return map[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const map: Record<string, string> = {
    critical: '严重',
    general: '一般',
    minor: '轻微',
  }
  return map[severity] || severity
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    confirmed: 'success',
    ignored: 'warning',
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    ignored: '已忽略',
  }
  return map[status] || status
}

// 查看详情
const viewDetail = async (row: Annotation) => {
  try {
    // 获取完整的标注详情
    const detail = await getAnnotation(row.id)
    currentAnnotation.value = detail
    showDetailDialog.value = true
  } catch (error) {
    ElMessage.error('获取标注详情失败')
  }
}

// 从详情页面打开编辑
const handleEditFromDetail = () => {
  if (currentAnnotation.value) {
    showDetailDialog.value = false
    editAnnotation(currentAnnotation.value)
  }
}

// 编辑标注
const editAnnotation = async (row: Annotation) => {
  try {
    // 获取完整的标注信息
    const detail = await getAnnotation(row.id)
    // 填充编辑表单
    editForm.value = {
      status: detail.status,
      severity: detail.severity,
      reason: detail.reason || '',
      suggestion: detail.suggestion || '',
    }
    currentAnnotation.value = detail
    showEditDialog.value = true
  } catch (error) {
    ElMessage.error('获取标注信息失败')
  }
}

// 保存编辑
const handleSaveEdit = async () => {
  if (!editFormRef.value || !currentAnnotation.value) return

  try {
    await editFormRef.value.validate()
    saving.value = true
    await updateAnnotation(currentAnnotation.value.id, editForm.value)
    ElMessage.success('保存成功')
    showEditDialog.value = false
    // 重新加载列表
    loadAnnotations()
    // 如果详情对话框打开，也更新详情
    if (showDetailDialog.value && currentAnnotation.value) {
      const updated = await getAnnotation(currentAnnotation.value.id)
      currentAnnotation.value = updated
    }
  } catch (error: any) {
    if (error !== false) {
      // 验证失败时 error 为 false，其他情况才是真正的错误
      ElMessage.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row: Annotation) => {
  try {
    await ElMessageBox.confirm('确定要删除这个标注吗？', '提示', { type: 'warning' })
    await deleteAnnotation(row.id)
    ElMessage.success('删除成功')
    loadAnnotations()
  } catch (error) {
    // 用户取消
  }
}

// 导出当前标注
const handleExportCurrent = () => {
  if (!currentAnnotation.value) return
  exportAnnotationsToJSON([currentAnnotation.value], `标注_${currentAnnotation.value.id}.json`)
}

// 导出全部标注
const handleExportAll = async () => {
  try {
    await ElMessageBox.confirm(
      '选择导出格式',
      '提示',
      {
        confirmButtonText: 'JSON格式',
        cancelButtonText: 'CSV格式',
        distinguishCancelAndClose: true,
        type: 'info',
      }
    )
    // 用户选择JSON格式
    exportAnnotationsToJSON(annotations.value)
  } catch (action: any) {
    if (action === 'cancel') {
      // 用户选择CSV格式
      exportAnnotationsToCSV(annotations.value)
    }
  }
}

onMounted(() => {
  loadAnnotations()
})
</script>

<style scoped>
.annotations-page {
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

:deep(.el-card__header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-card__header span) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-actions {
  display: flex;
  gap: 10px;
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

:deep(.el-pagination) {
  margin-top: 20px;
  justify-content: flex-end;
}

/* 详情对话框样式 */
.annotation-detail {
  padding: 10px 0;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.content-card {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

.content-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  color: #606266;
  min-height: 60px;
  padding: 12px;
}

.highlight-content {
  position: relative;
}

.highlight-text {
  background: linear-gradient(120deg, #fff3cd 0%, #ffe69c 100%);
  padding: 2px 4px;
  border-radius: 3px;
  border-left: 3px solid #ffc107;
  font-weight: 500;
}

.position-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.position-info .el-icon {
  font-size: 14px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
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
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}
</style>

