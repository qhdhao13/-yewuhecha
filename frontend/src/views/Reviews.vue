<template>
  <div class="reviews-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合规审查</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建审查任务
          </el-button>
        </div>
      </template>

      <!-- 审查记录列表 -->
      <el-table :data="reviews" v-loading="loading" style="margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="document_id" label="文档ID" width="100" />
        <el-table-column prop="regulation_id" label="制度ID" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_issues" label="不符合项" width="100" />
        <el-table-column label="严重程度" width="200">
          <template #default="{ row }">
            <span>严重: {{ row.critical_count }}</span>
            <span style="margin: 0 10px">一般: {{ row.general_count }}</span>
            <span>轻微: {{ row.minor_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="review_time" label="审查时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看详情</el-button>
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
        @size-change="loadReviews"
        @current-change="loadReviews"
      />
    </el-card>

    <!-- 创建审查对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建审查任务" width="500px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="员工文档" required>
          <el-select v-model="reviewForm.document_id" placeholder="请选择文档" style="width: 100%">
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.name"
              :value="doc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="制度文件" required>
          <el-select v-model="reviewForm.regulation_id" placeholder="请选择制度" style="width: 100%">
            <el-option
              v-for="reg in regulations"
              :key="reg.id"
              :label="reg.name"
              :value="reg.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="审查人">
          <el-input v-model="reviewForm.reviewer" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 审查详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="审查详情"
      width="1200px"
      :close-on-click-modal="false"
    >
      <div v-if="currentReview" class="review-detail" v-loading="detailLoading">
        <!-- 审查基本信息 -->
        <el-card shadow="never" class="info-card">
          <template #header>
            <span>审查信息</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="审查ID">{{ currentReview.id }}</el-descriptions-item>
            <el-descriptions-item label="审查状态">
              <el-tag :type="getStatusType(currentReview.status)">
                {{ getStatusText(currentReview.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审查人">
              {{ currentReview.reviewer || '未指定' }}
            </el-descriptions-item>
            <el-descriptions-item label="员工文档">
              {{ documentInfo?.name || `文档ID: ${currentReview.document_id}` }}
            </el-descriptions-item>
            <el-descriptions-item label="制度文件">
              {{ regulationInfo?.name || `制度ID: ${currentReview.regulation_id}` }}
            </el-descriptions-item>
            <el-descriptions-item label="审查时间">
              {{ new Date(currentReview.review_time).toLocaleString('zh-CN') }}
            </el-descriptions-item>
            <el-descriptions-item label="完成时间" v-if="currentReview.completed_time">
              {{ new Date(currentReview.completed_time).toLocaleString('zh-CN') }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 统计信息 -->
        <el-card shadow="never" class="info-card" style="margin-top: 20px">
          <template #header>
            <span>统计信息</span>
          </template>
          <div class="statistics">
            <div class="stat-item">
              <div class="stat-value">{{ currentReview.total_issues }}</div>
              <div class="stat-label">不符合项总数</div>
            </div>
            <div class="stat-item critical">
              <div class="stat-value">{{ currentReview.critical_count }}</div>
              <div class="stat-label">严重</div>
            </div>
            <div class="stat-item general">
              <div class="stat-value">{{ currentReview.general_count }}</div>
              <div class="stat-label">一般</div>
            </div>
            <div class="stat-item minor">
              <div class="stat-value">{{ currentReview.minor_count }}</div>
              <div class="stat-label">轻微</div>
            </div>
          </div>
        </el-card>

        <!-- 标注列表 -->
        <el-card shadow="never" class="info-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>标注列表</span>
              <div class="header-actions">
                <el-select
                  v-model="annotationFilter.severity"
                  placeholder="严重程度"
                  clearable
                  style="width: 120px; margin-right: 10px"
                  @change="loadAnnotations"
                >
                  <el-option label="严重" value="critical" />
                  <el-option label="一般" value="general" />
                  <el-option label="轻微" value="minor" />
                </el-select>
                <el-select
                  v-model="annotationFilter.status"
                  placeholder="状态"
                  clearable
                  style="width: 120px"
                  @change="loadAnnotations"
                >
                  <el-option label="待确认" value="pending" />
                  <el-option label="已确认" value="confirmed" />
                  <el-option label="已忽略" value="ignored" />
                </el-select>
              </div>
            </div>
          </template>
          <el-table
            :data="reviewAnnotations"
            v-loading="annotationsLoading"
            style="margin-top: 10px"
            max-height="400"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="issue_type" label="问题类型" width="120">
              <template #default="{ row }">
                <el-tag>{{ getIssueTypeText(row.issue_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">
                  {{ getSeverityText(row.severity) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="不符合内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getAnnotationStatusType(row.status)">
                  {{ getAnnotationStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewAnnotationDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button
          type="success"
          @click="handleExportReview"
          :disabled="!currentReview || reviewAnnotations.length === 0"
        >
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Download } from '@element-plus/icons-vue'
import { getReviews, getReview, createReview, type Review } from '@/api/reviews'
import { getDocuments, getDocument, type Document } from '@/api/documents'
import { getRegulations, getRegulation, type Regulation } from '@/api/regulations'
import { getAnnotations, type Annotation } from '@/api/annotations'
import { exportReviewReport } from '@/utils/export'

const loading = ref(false)
const reviews = ref<Review[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showCreateDialog = ref(false)
const creating = ref(false)
const reviewForm = ref({
  document_id: 0,
  regulation_id: 0,
  reviewer: '',
})
const documents = ref<Document[]>([])
const regulations = ref<Regulation[]>([])

// 详情对话框
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const currentReview = ref<Review | null>(null)
const documentInfo = ref<Document | null>(null)
const regulationInfo = ref<Regulation | null>(null)

// 标注列表
const annotationsLoading = ref(false)
const reviewAnnotations = ref<Annotation[]>([])
const annotationFilter = ref({
  severity: '',
  status: '',
})

const loadReviews = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    const data = await getReviews(params)
    reviews.value = Array.isArray(data) ? data : []
    total.value = reviews.value.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const loadDocumentsAndRegulations = async () => {
  try {
    const [docsData, regsData] = await Promise.all([
      getDocuments({ limit: 1000 }),
      getRegulations({ limit: 1000 }),
    ])
    // API返回格式是 { items: [...], total: ... }
    documents.value = docsData && 'items' in docsData ? docsData.items : (Array.isArray(docsData) ? docsData : [])
    regulations.value = regsData && 'items' in regsData ? regsData.items : (Array.isArray(regsData) ? regsData : [])
  } catch (error) {
    console.error('加载选项失败:', error)
    ElMessage.error('加载选项失败')
  }
}

const handleCreate = async () => {
  if (!reviewForm.value.document_id || !reviewForm.value.regulation_id) {
    ElMessage.warning('请选择文档和制度')
    return
  }
  creating.value = true
  try {
    await createReview(reviewForm.value)
    ElMessage.success('审查任务已创建')
    showCreateDialog.value = false
    reviewForm.value = { document_id: 0, regulation_id: 0, reviewer: '' }
    loadReviews()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

// 标注相关工具函数
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

const getAnnotationStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    confirmed: 'success',
    ignored: 'warning',
  }
  return map[status] || 'info'
}

const getAnnotationStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    ignored: '已忽略',
  }
  return map[status] || status
}

// 查看审查详情
const viewDetail = async (row: Review) => {
  try {
    detailLoading.value = true
    showDetailDialog.value = true

    // 获取完整的审查详情
    const reviewDetail = await getReview(row.id)
    currentReview.value = reviewDetail

    // 并行加载关联的文档和制度信息
    const [doc, reg] = await Promise.all([
      getDocument(reviewDetail.document_id).catch(() => null),
      getRegulation(reviewDetail.regulation_id).catch(() => null),
    ])
    documentInfo.value = doc
    regulationInfo.value = reg

    // 加载该审查的标注列表
    await loadAnnotations()
  } catch (error) {
    ElMessage.error('获取审查详情失败')
    showDetailDialog.value = false
  } finally {
    detailLoading.value = false
  }
}

// 加载标注列表
const loadAnnotations = async () => {
  if (!currentReview.value) return

  annotationsLoading.value = true
  try {
    const params: any = {
      review_id: currentReview.value.id,
      limit: 1000, // 获取所有标注
    }
    if (annotationFilter.value.severity) {
      params.severity = annotationFilter.value.severity
    }
    if (annotationFilter.value.status) {
      params.status = annotationFilter.value.status
    }
    const data = await getAnnotations(params)
    reviewAnnotations.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载标注列表失败')
  } finally {
    annotationsLoading.value = false
  }
}

// 查看标注详情（跳转到标注管理页面）
const viewAnnotationDetail = (annotation: Annotation) => {
  ElMessage.info('请前往标注管理页面查看详情')
  // 可以在这里实现路由跳转或打开标注详情对话框
}

// 导出审查报告
const handleExportReview = () => {
  if (!currentReview.value) return
  exportReviewReport(
    currentReview.value,
    reviewAnnotations.value,
    documentInfo.value?.name,
    regulationInfo.value?.name
  )
}

// 监听创建对话框打开，自动加载文档和制度列表
watch(showCreateDialog, (newVal) => {
  if (newVal) {
    loadDocumentsAndRegulations()
  }
})

onMounted(() => {
  loadReviews()
  loadDocumentsAndRegulations()
})
</script>

<style scoped>
.reviews-page {
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

/* 详情对话框样式 */
.review-detail {
  padding: 10px 0;
}

.info-card {
  border: 1px solid #ebeef5;
}

.info-card :deep(.el-card__header) {
  background-color: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
  padding: 12px 16px;
}

.info-card :deep(.el-card__header span) {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card .header-actions {
  display: flex;
  align-items: center;
}

.statistics {
  display: flex;
  gap: 30px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.stat-item.critical .stat-value {
  color: #f56c6c;
}

.stat-item.general .stat-value {
  color: #e6a23c;
}

.stat-item.minor .stat-value {
  color: #909399;
}

.stat-label {
  font-size: 14px;
  color: #909399;
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
  max-height: 80vh;
  overflow-y: auto;
}

:deep(.el-dialog__footer) {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}
</style>

