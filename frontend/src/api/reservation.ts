import request from '@/utils/request'

export interface ReservationItem {
  id: number
  user_id: number
  user_name: string
  lab_id: number
  lab_name: string
  device_id: number | null
  device_name: string
  date: string
  start_time: string | null
  end_time: string | null
  remark: string | null
  status: number
  create_time: string
}

export interface ReservationListResult {
  total: number
  list: ReservationItem[]
}

export interface ReservationCreateParams {
  lab_id: number
  device_id?: number | null
  date: string
  start_time?: string | null
  end_time?: string | null
  remark?: string | null
}

/** 创建预约 */
export function createReservation(data: ReservationCreateParams) {
  return request.post<unknown, ReservationItem>('/reservations', data)
}

/** 我的预约列表(分页+状态筛选) */
export function getMyReservations(params: {
  status?: number | null
  page: number
  page_size: number
}) {
  return request.get<unknown, ReservationListResult>('/reservations', { params })
}

/** 管理员-全部预约列表(分页+状态+关键词筛选) */
export function getAllReservations(params: {
  status?: number | null
  keyword?: string
  page: number
  page_size: number
}) {
  return request.get<unknown, ReservationListResult>('/reservations/all', { params })
}

/** 取消我的预约(仅待审核) */
export function cancelReservation(id: number) {
  return request.put<unknown, null>(`/reservations/${id}/cancel`)
}

/** 管理员审核预约(2通过/3拒绝) */
export function auditReservation(id: number, status: number) {
  return request.put<unknown, null>(`/reservations/${id}/audit`, { status })
}
