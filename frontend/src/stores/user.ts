import { defineStore } from 'pinia'
import { getUserInfo, type UserInfo } from '@/api/auth'

interface UserState {
  user: UserInfo | null
  /** 本次会话是否已通过 /me 加载过用户(刷新页面后重置为 false) */
  loaded: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    loaded: false
  }),
  actions: {
    /** 调用 /me 校验 token 并恢复用户信息,整次会话仅在首次(刷新后)执行 */
    async fetchUser() {
      this.user = await getUserInfo()
      this.loaded = true
    },
    /** 登录成功后直接写入,无需再请求 /me */
    setUser(user: UserInfo) {
      this.user = user
      this.loaded = true
    },
    /** 修改个人信息后局部更新 */
    updateUser(patch: Partial<UserInfo>) {
      if (this.user) this.user = { ...this.user, ...patch }
    },
    reset() {
      this.user = null
      this.loaded = false
    }
  }
})
