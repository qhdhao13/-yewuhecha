/**
 * 制度文件API
 * 提供制度文件相关的API调用方法
 */
import request from './request'

export interface Regulation {
  id: number
  name: string
  code?: string
  type?: string
  effective_date?: string
  file_path: string
  file_type: string
  file_size?: number
  upload_time: string
  uploader?: string
}

export interface RegulationCreateParams {
  name: string
  code?: string
  type?: string
  effective_date?: string
  uploader?: string
}

/**
 * 获取制度文件列表
 */
export const getRegulations = (params?: {
  skip?: number
  limit?: number
  type?: string
  search?: string
}) => {
  return request.get<{ items: Regulation[]; total: number }>('/regulations/', { params })
}

/**
 * 获取制度文件详情
 */
export const getRegulation = (id: number) => {
  return request.get<Regulation>(`/regulations/${id}`)
}

/**
 * 上传制度文件
 */
export const uploadRegulation = (formData: FormData) => {
  return request.post<Regulation>('/regulations/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 更新制度文件信息
 */
export const updateRegulation = (id: number, data: Partial<RegulationCreateParams>) => {
  return request.put<Regulation>(`/regulations/${id}`, data)
}

/**
 * 删除制度文件
 */
export const deleteRegulation = (id: number) => {
  return request.delete(`/regulations/${id}`)
}

