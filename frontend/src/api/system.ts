/**
 * 系统状态API
 */
import request from './request'

export interface SystemStatus {
  ollama_service: boolean
  llm_model: boolean
  embedding_model: boolean
  llm_model_name: string
  embedding_model_name: string
  ollama_url: string
  message: string
}

export interface ModelInfo {
  name: string
  size: number
  modified_at: string
}

export interface ModelsResponse {
  success: boolean
  message?: string
  models: ModelInfo[]
}

/**
 * 获取系统状态
 */
export const getSystemStatus = () => {
  return request.get<SystemStatus>('/system/status')
}

/**
 * 获取可用模型列表
 */
export const getAvailableModels = () => {
  return request.get<ModelsResponse>('/system/models')
}

