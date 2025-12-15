/**
 * 合规审查API
 */
import request from './request'

export interface Review {
  id: number
  document_id: number
  regulation_id: number
  status: string
  total_issues: number
  critical_count: number
  general_count: number
  minor_count: number
  review_time: string
  completed_time?: string
  reviewer?: string
}

export interface ReviewCreateParams {
  document_id: number
  regulation_id: number
  reviewer?: string
}

/**
 * 创建审查任务
 */
export const createReview = (data: ReviewCreateParams) => {
  return request.post<Review>('/reviews/', data)
}

/**
 * 获取审查记录列表
 */
export const getReviews = (params?: {
  skip?: number
  limit?: number
  document_id?: number
  regulation_id?: number
  status?: string
}) => {
  return request.get<Review[]>('/reviews/', { params })
}

/**
 * 获取审查记录详情
 */
export const getReview = (id: number) => {
  return request.get<Review>(`/reviews/${id}`)
}

