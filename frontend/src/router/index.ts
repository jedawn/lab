import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

declare module 'vue-router' {
  interface RouteMeta {
    /** 菜单与面包屑标题 */
    title?: string
    /** 菜单图标（element-plus icons 组件名） */
    icon?: string
    /** 是否在菜单中隐藏 */
    hidden?: boolean
    /** 当前路由激活的菜单项路径（用于详情页联动菜单高亮） */
    activeMenu?: string
    /** 允许访问的角色列表，为空则不限 */
    roles?: string[]
  }
}

/**
 * 布局路由：Home.vue 作为整体框架（侧边菜单 + 顶栏 + 内容区）。
 * 菜单由 children 中的 meta（title/icon/hidden）动态生成，
 * 新增页面只需在此添加一条路由记录。
 */
export const layoutRoute: RouteRecordRaw = {
  path: '/',
  name: 'layout',
  component: () => import('@/views/Home.vue'),
  redirect: '/dashboard',
  children: [
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { title: '系统首页', icon: 'HomeFilled' }
    },
    {
      path: '/lab',
      name: 'lab',
      component: () => import('@/views/LabList.vue'),
      meta: { title: '实验室', icon: 'OfficeBuilding' }
    },
    {
      path: '/lab/manage',
      name: 'lab-manage',
      component: () => import('@/views/LabManage.vue'),
      meta: { title: '实验室管理', icon: 'Setting', roles: ['admin'] }
    },
    {
      path: '/lab/:id',
      name: 'lab-detail',
      component: () => import('@/views/LabDetail.vue'),
      meta: { title: '实验室详情', hidden: true, activeMenu: '/lab' }
    },
    {
      path: '/reservation',
      name: 'my-reservation',
      component: () => import('@/views/MyReservations.vue'),
      meta: { title: '我的预约', icon: 'Calendar' }
    },
    {
      path: '/reservation/audit',
      name: 'reservation-audit',
      component: () => import('@/views/ReservationAudit.vue'),
      meta: { title: '预约审核', icon: 'Finished', roles: ['admin'] }
    },
    {
      path: '/device',
      name: 'device',
      component: () => import('@/views/DeviceManage.vue'),
      meta: { title: '设备列表管理', icon: 'Box', roles: ['admin'] }
    },
    {
      path: '/user',
      name: 'user',
      component: () => import('@/views/UserManage.vue'),
      meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
    }
  ]
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },
    layoutRoute,
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
  ]
})

/** 免登录页面 */
const publicPaths = ['/login', '/register']

/**
 * 路由守卫:
 * - 未登录访问业务页 → 跳登录页;已登录访问登录/注册页 → 跳首页
 * - 刷新页面后 Pinia 内存重置(loaded=false),有 token 时只调用一次 /me 校验并恢复用户;
 *   之后纯前端路由切换 loaded=true,不再请求。
 */
router.beforeEach(async (to) => {
  const token = localStorage.getItem('token')

  if (publicPaths.includes(to.path)) {
    return token ? '/dashboard' : true
  }
  if (!token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  const userStore = useUserStore()
  if (!userStore.loaded) {
    try {
      await userStore.fetchUser()
    } catch {
      // /me 失败(token 过期/无效或后端不可用):清凭证,打破 /login↔/dashboard 循环
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      userStore.reset()
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }
  // 角色权限校验:meta.roles 限制的页面,非允许角色跳回首页
  const roles = to.meta?.roles as string[] | undefined
  if (roles && roles.length && !roles.includes(userStore.user?.role ?? '')) {
    return '/dashboard'
  }
  return true
})

export default router
