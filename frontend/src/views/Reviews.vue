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
      width="1400px"
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
          <!-- 标注列表 - 使用卡片式布局展示问题和建议 -->
          <div v-if="reviewAnnotations.length === 0" class="empty-annotations">
            <el-empty description="暂无标注" />
          </div>
          <div v-else class="annotations-list">
            <el-card
              v-for="annotation in reviewAnnotations"
              :key="annotation.id"
              shadow="hover"
              class="annotation-card"
              :class="`severity-${annotation.severity}`"
            >
              <template #header>
                <div class="annotation-header">
                  <div class="header-left">
                    <el-tag :type="getSeverityType(annotation.severity)" size="large">
                      {{ getSeverityText(annotation.severity) }}
                    </el-tag>
                    <el-tag style="margin-left: 8px">{{ getIssueTypeText(annotation.issue_type) }}</el-tag>
                    <span class="annotation-id">#{{ annotation.id }}</span>
                  </div>
                  <div class="header-right">
                    <el-tag :type="getAnnotationStatusType(annotation.status)" size="small">
                      {{ getAnnotationStatusText(annotation.status) }}
                    </el-tag>
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click="toggleAnnotationDetail(annotation.id)"
                      style="margin-left: 8px"
                    >
                      {{ expandedAnnotations.has(annotation.id) ? '收起' : '展开' }}
                    </el-button>
                  </div>
                </div>
              </template>

              <!-- 问题内容 -->
              <div class="annotation-content">
                <div class="content-section">
                  <h4 class="section-title">
                    <el-icon><Warning /></el-icon>
                    不符合内容
                  </h4>
                  <div class="content-text highlight-text">
                    {{ annotation.content || '未指定' }}
                  </div>
                </div>

                <div class="content-section" v-if="annotation.regulation_clause">
                  <h4 class="section-title">
                    <el-icon><Document /></el-icon>
                    对应制度条款
                  </h4>
                  <div class="content-text">
                    {{ annotation.regulation_clause }}
                  </div>
                </div>

                <!-- 展开的详细信息 -->
                <Transition name="slide-fade">
                  <div v-if="expandedAnnotations.has(annotation.id)" class="annotation-details">
                    <!-- 不符合原因 -->
                    <div class="content-section" v-if="annotation.reason || annotationAISuggestions[annotation.id]?.reason">
                      <h4 class="section-title">
                        <el-icon><InfoFilled /></el-icon>
                        不符合原因
                      </h4>
                      <div class="content-text">
                        {{ annotationAISuggestions[annotation.id]?.reason || annotation.reason || '暂无说明' }}
                      </div>
                    </div>

                    <!-- 修改建议 -->
                    <div class="content-section">
                      <h4 class="section-title">
                        <el-icon><QuestionFilled /></el-icon>
                        修改建议
                        <el-button
                          link
                          type="primary"
                          size="small"
                          :loading="generatingSuggestions.has(annotation.id)"
                          @click="generateSuggestion(annotation)"
                          style="margin-left: 8px"
                        >
                          <el-icon><MagicStick /></el-icon>
                          {{ annotationAISuggestions[annotation.id] ? '重新生成' : 'AI生成建议' }}
                        </el-button>
                      </h4>
                      <div class="content-text suggestion-text">
                        <div v-if="annotationAISuggestions[annotation.id]?.suggestion">
                          {{ annotationAISuggestions[annotation.id].suggestion }}
                        </div>
                        <div v-else-if="annotation.suggestion">
                          {{ annotation.suggestion }}
                        </div>
                        <div v-else class="no-suggestion">
                          暂无建议，点击"AI生成建议"获取智能改进方案
                        </div>
                      </div>
                    </div>

                    <!-- 详细分析（AI生成） -->
                    <div class="content-section" v-if="annotationAISuggestions[annotation.id]?.detailed_analysis">
                      <h4 class="section-title">
                        <el-icon><Reading /></el-icon>
                        详细分析
                      </h4>
                      <div class="content-text analysis-text">
                        {{ annotationAISuggestions[annotation.id].detailed_analysis }}
                      </div>
                    </div>

                    <!-- 改进后的内容示例（AI生成） -->
                    <div class="content-section" v-if="annotationAISuggestions[annotation.id]?.improved_content">
                      <h4 class="section-title">
                        <el-icon><EditPen /></el-icon>
                        改进示例
                      </h4>
                      <div class="content-text improved-content">
                        {{ annotationAISuggestions[annotation.id].improved_content }}
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </el-card>
          </div>
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
import { ref, onMounted, watch, Transition } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Download, Warning, Document, InfoFilled, EditPen, QuestionFilled, MagicStick, Reading } from '@element-plus/icons-vue'
import { getReviews, getReview, createReview, type Review } from '@/api/reviews'
import { getDocuments, getDocument, type Document as DocumentType } from '@/api/documents'
import { getRegulations, getRegulation, type Regulation as RegulationType } from '@/api/regulations'
import { getAnnotations, generateAISuggestion, type Annotation, type AISuggestionResponse } from '@/api/annotations'
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
const documents = ref<DocumentType[]>([])
const regulations = ref<RegulationType[]>([])

// 详情对话框
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const currentReview = ref<Review | null>(null)
const documentInfo = ref<DocumentType | null>(null)
const regulationInfo = ref<RegulationType | null>(null)

// 标注列表
const annotationsLoading = ref(false)
const reviewAnnotations = ref<Annotation[]>([])
const annotationFilter = ref({
  severity: '',
  status: '',
})

// 展开的标注ID集合
const expandedAnnotations = ref<Set<number>>(new Set())

// AI建议数据
const annotationAISuggestions = ref<Record<number, AISuggestionResponse>>({})

// 正在生成建议的标注ID集合
const generatingSuggestions = ref<Set<number>>(new Set())

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
    // 重置展开状态和AI建议
    expandedAnnotations.value.clear()
    annotationAISuggestions.value = {}
  } catch (error) {
    ElMessage.error('加载标注列表失败')
  } finally {
    annotationsLoading.value = false
  }
}

// 切换标注详情展开/收起
const toggleAnnotationDetail = (annotationId: number) => {
  if (expandedAnnotations.value.has(annotationId)) {
    expandedAnnotations.value.delete(annotationId)
  } else {
    expandedAnnotations.value.add(annotationId)
  }
}

// 生成AI改进建议
const generateSuggestion = async (annotation: Annotation) => {
  generatingSuggestions.value.add(annotation.id)
  try {
    const result = await generateAISuggestion(annotation.id)
    if (result.success) {
      annotationAISuggestions.value[annotation.id] = result
      // 如果建议已生成，自动展开
      if (!expandedAnnotations.value.has(annotation.id)) {
        expandedAnnotations.value.add(annotation.id)
      }
      ElMessage.success('AI建议生成成功')
    } else {
      ElMessage.warning('生成建议失败，请稍后重试')
    }
  } catch (error) {
    console.error('生成AI建议失败:', error)
    ElMessage.error('生成AI建议失败')
  } finally {
    generatingSuggestions.value.delete(annotation.id)
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

/* 标注列表样式 */
.empty-annotations {
  padding: 40px 0;
  text-align: center;
}

.annotations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 10px;
}

.annotation-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.annotation-card.severity-critical {
  border-left: 4px solid #f56c6c;
}

.annotation-card.severity-general {
  border-left: 4px solid #e6a23c;
}

.annotation-card.severity-minor {
  border-left: 4px solid #909399;
}

.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.annotation-id {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

.header-right {
  display: flex;
  align-items: center;
}

.annotation-content {
  padding: 0;
}

.content-section {
  margin-bottom: 20px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.content-text {
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}

.highlight-text {
  background: linear-gradient(120deg, #fff3cd 0%, #ffe69c 100%);
  border-left: 3px solid #ffc107;
  font-weight: 500;
}

.suggestion-text {
  background: linear-gradient(120deg, #d1ecf1 0%, #bee5eb 100%);
  border-left: 3px solid #17a2b8;
}

.analysis-text {
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
}

.improved-content {
  background: linear-gradient(120deg, #d4edda 0%, #c3e6cb 100%);
  border-left: 3px solid #28a745;
  font-style: italic;
}

.no-suggestion {
  color: #909399;
  font-style: italic;
  text-align: center;
  padding: 20px;
}

.annotation-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  background-color: #fafafa;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>

