/**
 * 标注管理API
 */
import request from './request'

export interface Annotation {
  id: number
  review_id: number
  document_id: number
  regulation_id: number
  position?: string
  start_pos?: number
  end_pos?: number
  content?: string
  regulation_clause?: string
  issue_type: string
  severity: string
  reason?: string
  suggestion?: string
  status: string
  create_time: string
  update_time: string
  reviewer?: string
}

export interface AnnotationUpdateParams {
  status?: string
  reason?: string
  suggestion?: string
  severity?: string
}

/**
 * 获取标注列表
 */
export const getAnnotations = (params?: {
  skip?: number
  limit?: number
  review_id?: number
  document_id?: number
  regulation_id?: number
  status?: string
  severity?: string
  issue_type?: string
}) => {
  return request.get<Annotation[]>('/annotations/', { params })
}

/**
 * 获取标注详情
 */
export const getAnnotation = (id: number) => {
  return request.get<Annotation>(`/annotations/${id}`)
}

/**
 * 更新标注
 */
export const updateAnnotation = (id: number, data: AnnotationUpdateParams) => {
  return request.put<Annotation>(`/annotations/${id}`, data)
}

/**
 * 删除标注
 */
export const deleteAnnotation = (id: number) => {
  return request.delete(`/annotations/${id}`)
}

