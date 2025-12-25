/**
 * 导出工具函数
 * 提供各种格式的导出功能
 */

import { ElMessage } from 'element-plus'
import type { Annotation } from '@/api/annotations'
import type { Review } from '@/api/reviews'

/**
 * 导出标注为JSON格式
 */
export const exportAnnotationsToJSON = (annotations: Annotation[], filename?: string) => {
  try {
    const dataStr = JSON.stringify(annotations, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename || `标注数据_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

/**
 * 导出标注为CSV格式
 */
export const exportAnnotationsToCSV = (annotations: Annotation[], filename?: string) => {
  try {
    // CSV表头
    const headers = [
      'ID',
      '审查记录ID',
      '文档ID',
      '制度ID',
      '问题类型',
      '严重程度',
      '不符合内容',
      '对应制度条款',
      '不符合原因',
      '修改建议',
      '状态',
      '位置',
      '创建时间',
    ]

    // 转换数据
    const rows = annotations.map((ann) => [
      ann.id.toString(),
      ann.review_id.toString(),
      ann.document_id.toString(),
      ann.regulation_id.toString(),
      getIssueTypeText(ann.issue_type),
      getSeverityText(ann.severity),
      ann.content || '',
      ann.regulation_clause || '',
      ann.reason || '',
      ann.suggestion || '',
      getStatusText(ann.status),
      ann.position || '',
      new Date(ann.create_time).toLocaleString('zh-CN'),
    ])

    // 组合CSV内容
    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')),
    ].join('\n')

    // 添加BOM以支持中文
    const BOM = '\uFEFF'
    const dataBlob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename || `标注数据_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

/**
 * 导出审查报告（包含审查信息和标注列表）
 */
export const exportReviewReport = (
  review: Review,
  annotations: Annotation[],
  documentName?: string,
  regulationName?: string,
  filename?: string
) => {
  try {
    const report = {
      审查信息: {
        审查ID: review.id,
        文档ID: review.document_id,
        文档名称: documentName || `文档ID: ${review.document_id}`,
        制度ID: review.regulation_id,
        制度名称: regulationName || `制度ID: ${review.regulation_id}`,
        审查状态: getReviewStatusText(review.status),
        审查人: review.reviewer || '未指定',
        审查时间: new Date(review.review_time).toLocaleString('zh-CN'),
        完成时间: review.completed_time
          ? new Date(review.completed_time).toLocaleString('zh-CN')
          : '未完成',
      },
      统计信息: {
        不符合项总数: review.total_issues,
        严重: review.critical_count,
        一般: review.general_count,
        轻微: review.minor_count,
      },
      标注列表: annotations.map((ann) => ({
        ID: ann.id,
        问题类型: getIssueTypeText(ann.issue_type),
        严重程度: getSeverityText(ann.severity),
        不符合内容: ann.content || '',
        对应制度条款: ann.regulation_clause || '',
        不符合原因: ann.reason || '',
        修改建议: ann.suggestion || '',
        状态: getStatusText(ann.status),
        位置: ann.position || '',
        创建时间: new Date(ann.create_time).toLocaleString('zh-CN'),
      })),
    }

    const dataStr = JSON.stringify(report, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename || `审查报告_${review.id}_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 工具函数
const getIssueTypeText = (type: string) => {
  const map: Record<string, string> = {
    content_mismatch: '内容不符',
    missing: '缺失',
    extra: '多余',
    format: '格式不符',
  }
  return map[type] || type
}

const getSeverityText = (severity: string) => {
  const map: Record<string, string> = {
    critical: '严重',
    general: '一般',
    minor: '轻微',
  }
  return map[severity] || severity
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    ignored: '已忽略',
  }
  return map[status] || status
}

const getReviewStatusText = (status: string) => {
  const map: Record<string, string> = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}
