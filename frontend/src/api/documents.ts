/**
 * 员工文档API
 */
import request from './request'

export interface Document {
  id: number
  name: string
  type?: string
  author?: string
  department?: string
  file_path: string
  file_type: string
  file_size?: number
  status: string
  upload_time: string
}

export interface DocumentCreateParams {
  name: string
  type?: string
  author?: string
  department?: string
}

/**
 * 获取员工文档列表
 */
export const getDocuments = (params?: {
  skip?: number
  limit?: number
  status?: string
  author?: string
  department?: string
  search?: string
}) => {
  return request.get<{ items: Document[]; total: number }>('/documents/', { params })
}

/**
 * 获取员工文档详情
 */
export const getDocument = (id: number) => {
  return request.get<Document>(`/documents/${id}`)
}

/**
 * 上传员工文档
 */
export const uploadDocument = (formData: FormData) => {
  return request.post<Document>('/documents/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 更新员工文档信息
 */
export const updateDocument = (id: number, data: Partial<DocumentCreateParams>) => {
  return request.put<Document>(`/documents/${id}`, data)
}

/**
 * 删除员工文档
 */
export const deleteDocument = (id: number) => {
  return request.delete(`/documents/${id}`)
}

