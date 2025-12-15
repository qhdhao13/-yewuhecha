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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getReviews, createReview, type Review } from '@/api/reviews'
import { getDocuments, type Document } from '@/api/documents'
import { getRegulations, type Regulation } from '@/api/regulations'

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
    documents.value = Array.isArray(docsData) ? docsData : []
    regulations.value = Array.isArray(regsData) ? regsData : []
  } catch (error) {
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

const viewDetail = (row: Review) => {
  ElMessage.info('查看详情功能开发中')
}

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
</style>

