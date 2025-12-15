<template>
  <div class="annotations-page">
    <el-card>
      <template #header>
        <span>标注管理</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAnnotations, deleteAnnotation, type Annotation } from '@/api/annotations'

const loading = ref(false)
const annotations = ref<Annotation[]>([])
const filterSeverity = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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

const viewDetail = (row: Annotation) => {
  ElMessage.info('查看详情功能开发中')
}

const editAnnotation = (row: Annotation) => {
  ElMessage.info('编辑功能开发中')
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

:deep(.el-card__header span) {
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

:deep(.el-pagination) {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

