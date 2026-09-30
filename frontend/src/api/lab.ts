import request from '@/utils/request'

export interface LabItem {
  id: number
  name: string
  intro: string | null
  cover: string | null
  location: string | null
  capacity: number
  open_start: string | null
  open_end: string | null
  status: number
  create_time: string
}

export interface LabListResult {
  total: number
  list: LabItem[]
}

export interface LabSaveParams {
  name: string
  intro?: string | null
  cover?: string | null
  location?: string | null
  capacity: number
  open_start?: string | null
  open_end?: string | null
  status: number
}

/** 实验室列表(分页+搜索) */
export function getLabs(params: { keyword?: string; page: number; page_size: number }) {
  return request.get<unknown, LabListResult>('/labs', { params })
}

/** 实验室详情 */
export function getLab(id: number | string) {
  return request.get<unknown, LabItem>(`/labs/${id}`)
}

/** 新增实验室 */
export function createLab(data: LabSaveParams) {
  return request.post<unknown, LabItem>('/labs', data)
}

/** 修改实验室 */
export function updateLab(id: number, data: LabSaveParams) {
  return request.put<unknown, LabItem>(`/labs/${id}`, data)
}

/** 删除实验室 */
export function deleteLab(id: number) {
  return request.delete<unknown, null>(`/labs/${id}`)
}
