import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/** 统一后端响应结构 */
interface ApiResult<T = unknown> {
  code: number
  message: string
  data: T
}

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

/** 错误弹窗去重:同一条消息在该时间窗口内只弹一次,避免后端不可用时满屏错误 */
const lastErrorMsg = { text: '', time: 0 }
const ERROR_DEDUP_MS = 3000

function showError(msg: string) {
  const now = Date.now()
  if (msg === lastErrorMsg.text && now - lastErrorMsg.time < ERROR_DEDUP_MS) {
    return
  }
  lastErrorMsg.text = msg
  lastErrorMsg.time = now
  ElMessage.error(msg)
}

/** 请求拦截器:自动携带 token */
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/** 响应拦截器:统一处理业务错误与 401 鉴权失效 */
request.interceptors.response.use(
  (response) => {
    const res = response.data as ApiResult
    // 直接返回业务数据(data 字段),非标准结构则原样返回
    if (res && typeof res === 'object' && 'code' in res && 'data' in res) {
      if (res.code !== 200) {
        if (res.code === 401) {
          // 业务码 401:token 过期/无效(使用过程中任意接口触发),清凭证并跳登录页
          localStorage.removeItem('token')
          localStorage.removeItem('userName')
          if (router.currentRoute.value.path !== '/login') {
            router.push('/login')
          }
        }
        showError(res.message || '请求失败')
        return Promise.reject(new Error(res.message || 'Error'))
      }
      return res.data
    }
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.response?.data?.message
    if (status === 401) {
      // 携带过期/无效 token 访问业务接口:登录态失效,清凭证并跳转登录页
      showError('登录状态已失效,请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    } else {
      // 网络错误/服务端异常(如后端停掉):去重提示,避免满屏弹窗
      showError(detail || error.message || '网络错误,请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request
export type { ApiResult }
