import request from '@/utils/request'

export interface UserListItem {
  id: number
  username: string
  name: string
  role: string
  email: string | null
  avatar: string | null
  phone: string | null
  status: number
  create_time: string
}

export interface UserListResult {
  total: number
  list: UserListItem[]
}

export interface UserCreateParams {
  username: string
  password: string
  name?: string | null
  role: string
  email?: string | null
  phone?: string | null
  status: number
}

export interface UserUpdateParams {
  name?: string | null
  role?: string | null
  email?: string | null
  phone?: string | null
  status?: number | null
  password?: string | null
}

/** 用户列表(分页+搜索) */
export function getUsers(params: {
  keyword?: string
  page: number
  page_size: number
}) {
  return request.get<unknown, UserListResult>('/users', { params })
}

/** 新增用户 */
export function createUser(data: UserCreateParams) {
  return request.post<unknown, UserListItem>('/users', data)
}

/** 修改用户 */
export function updateUser(id: number, data: UserUpdateParams) {
  return request.put<unknown, UserListItem>(`/users/${id}`, data)
}

/** 删除用户 */
export function deleteUser(id: number) {
  return request.delete<unknown, null>(`/users/${id}`)
}
