/**
 * 文件访问API
 */
import request from './request'

/**
 * 下载制度文件
 */
export const downloadRegulation = (regulationId: number) => {
  return request.get(`/files/regulations/${regulationId}/download`, {
    responseType: 'blob',
  })
}

/**
 * 下载员工文档
 */
export const downloadDocument = (documentId: number) => {
  return request.get(`/files/documents/${documentId}/download`, {
    responseType: 'blob',
  })
}

/**
 * 获取文件预览URL
 */
export const getFilePreviewUrl = (type: 'regulation' | 'document', id: number) => {
  return `/api/v1/files/${type === 'regulation' ? 'regulations' : 'documents'}/${id}/download`
}
