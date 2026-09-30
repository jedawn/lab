import request from '@/utils/request'

export interface DeviceItem {
  id: number
  name: string
  image: string | null
  model_spec: string | null
  quantity: number
  status: number
  lab_id: number
  lab_name: string
  create_time: string
}

export interface DeviceListResult {
  total: number
  list: DeviceItem[]
}

export interface DeviceSaveParams {
  name: string
  image?: string | null
  model_spec?: string | null
  quantity: number
  status: number
  lab_id: number
}

export interface LabOption {
  id: number
  name: string
}

/** 设备列表(分页+搜索+实验室筛选) */
export function getDevices(params: {
  keyword?: string
  lab_id?: number | null
  page: number
  page_size: number
}) {
  return request.get<unknown, DeviceListResult>('/devices', { params })
}

/** 新增设备 */
export function createDevice(data: DeviceSaveParams) {
  return request.post<unknown, DeviceItem>('/devices', data)
}

/** 修改设备 */
export function updateDevice(id: number, data: DeviceSaveParams) {
  return request.put<unknown, DeviceItem>(`/devices/${id}`, data)
}

/** 删除设备 */
export function deleteDevice(id: number) {
  return request.delete<unknown, null>(`/devices/${id}`)
}

/** 获取全部实验室(用于下拉选择) */
export async function getLabOptions(): Promise<LabOption[]> {
  const res = await request.get<unknown, { total: number; list: LabOption[] }>('/labs', {
    params: { page: 1, page_size: 100 }
  })
  return res.list
}
