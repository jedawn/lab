import request from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
  email: string | null
  avatar: string | null
  phone: string | null
}

export interface LoginResult {
  token: string
  user: UserInfo
}

export interface RegisterParams {
  username: string
  password: string
  confirm_password: string
}

export interface ProfileUpdateParams {
  name: string
  email: string | null
  avatar: string | null
  phone: string | null
}

export interface PasswordChangeParams {
  old_password: string
  new_password: string
  confirm_password: string
}

/** 用户登录 */
export function login(data: LoginParams) {
  return request.post<unknown, LoginResult>('/auth/login', data)
}

/** 用户注册 */
export function register(data: RegisterParams) {
  return request.post<unknown, null>('/auth/register', data)
}

/** 获取当前登录用户信息(校验 token 是否有效) */
export function getUserInfo() {
  return request.get<unknown, UserInfo>('/auth/me')
}

/** 修改当前用户个人信息 */
export function updateProfile(data: ProfileUpdateParams) {
  return request.put<unknown, UserInfo>('/auth/profile', data)
}

/** 修改当前用户密码 */
export function changePassword(data: PasswordChangeParams) {
  return request.put<unknown, null>('/auth/password', data)
}
